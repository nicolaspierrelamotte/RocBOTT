"""Témoin à dérive nulle et test de puissance par avantage planté.

Un *pipeline* est ici une paire :
- ``signal(bars) -> np.ndarray`` : ±1/0 à la clôture de chaque barre ;
- des paramètres de simulation (stop, objectif, durée, coûts, filtre).

``Pipeline.decide(bars)`` compose signal ET filtre de population par la même
fonction que la boucle de simulation (``lab.simulate.decisions``) : c'est
l'objet que ``lab.acausality.detect_leak`` doit recevoir (F-2).

Témoin à dérive nulle
---------------------
Le pipeline tourne sur des marches aléatoires sans dérive. Le R moyen attendu
n'est PAS supposé égal à -péage / stop (faux dès que stop ≠ objectif, à cause
des conventions d'exécution, F-4) : il est CALCULÉ en rejouant la même
mécanique (mêmes stop, objectif, durée, coûts, mêmes instants de décision) avec
un sens tiré à pile ou face, indépendant des prix. Ce que le témoin teste est
alors l'écart R - R attendu (``excess_r``, ``t_excess``, t de Student d'un
échantillon), jamais le R brut dont le péage tire le t vers le négatif (F-5).

Choix documenté du filtre de population dans la référence (``reference_filter``) :
« none » (défaut) rejoue la référence SANS le filtre du pipeline. Raison : un
filtre qui regarde le futur (cas de Colibri) sélectionne des trades dont le R
est meilleur QUEL QUE SOIT le sens ; une référence qui l'applique absorberait ce
biais et cacherait la fuite au témoin. Contrepartie : un filtre causal qui
change la composition des trades déplace légèrement le R attendu (c'est un
écart de mécanique, non une fuite) ; ``reference_filter="pipeline"`` le mesure.
Les deux sont publiés par ``zero_drift_control`` (``excess_r`` et
``excess_r_filtered_ref``).

Test de puissance
-----------------
``power_curve`` plante un avantage PAR TRADE (``edge_bp`` de rendement
additionnel par trade, étalé sur les barres où la position est tenue, dans le
sens de la position) et rapporte, pour un NOMBRE DE TRADES donné et sur
``n_reps`` répétitions indépendantes, une probabilité de détection avec son
intervalle de Wilson, à côté de l'avantage réalisé mesuré sur les trades.
"""
from __future__ import annotations

import hashlib
import inspect
import json
from dataclasses import dataclass
from pathlib import Path
from statistics import NormalDist
from typing import Callable, Sequence

import numpy as np

from .simulate import ACAUSAL_FILTERS, PopulationFilter, Trade, decisions, r_stats, simulate_trades
from .synthetic import Bars, random_walk_bars

Signal = Callable[[Bars], np.ndarray]


class InconclusiveError(ValueError):
    """Le témoin ou le détecteur n'a rien mesuré : une pièce ne doit pas être écrite."""


def _fn_id(fn) -> str:
    if fn is None:
        return "none"
    name = getattr(fn, "__qualname__", repr(fn))
    try:
        body = inspect.getsource(fn)
    except (OSError, TypeError):
        code = getattr(fn, "__code__", None)
        body = repr((code.co_code, code.co_consts)) if code is not None else repr(fn)
    return f"{name}:{hashlib.sha256(body.encode()).hexdigest()[:10]}"


@dataclass(frozen=True)
class Pipeline:
    signal: Signal
    stop_bp: float
    target_bp: float
    max_hold: int
    spread_bp: float = 0.0
    population_filter: PopulationFilter | None = None
    half_spread_bp: float | np.ndarray = 0.0
    swap_long_bp: float = 0.0
    swap_short_bp: float = 0.0
    stop_slippage_bp: float = 0.0
    name: str = ""
    allow_known_acausal: bool = False

    def __post_init__(self):
        # Garde, pas preuve (F-27) : un filtre connu pour regarder le futur n'entre
        # dans une chaîne que si l'appelant le demande explicitement (tests de détection).
        if self.population_filter in ACAUSAL_FILTERS and not self.allow_known_acausal:
            raise ValueError(
                "filtre de population connu comme acausal ; passer allow_known_acausal=True "
                "uniquement pour un test de détection"
            )

    def _sim_kwargs(self) -> dict:
        return dict(
            stop_bp=self.stop_bp,
            target_bp=self.target_bp,
            max_hold=self.max_hold,
            spread_bp=self.spread_bp,
            half_spread_bp=self.half_spread_bp,
            swap_long_bp=self.swap_long_bp,
            swap_short_bp=self.swap_short_bp,
            stop_slippage_bp=self.stop_slippage_bp,
        )

    def decide(self, bars: Bars) -> np.ndarray:
        """Décision par barre, signal ET filtre composés comme ``simulate_trades`` les applique."""
        return decisions(bars, self.signal(bars), self.population_filter)

    def run_trades(self, bars: Bars, *, signal: np.ndarray | None = None, with_filter: bool = True) -> list[Trade]:
        sig = self.signal(bars) if signal is None else signal
        return simulate_trades(
            bars, sig, population_filter=self.population_filter if with_filter else None, **self._sim_kwargs()
        )

    def run(self, bars: Bars) -> dict[str, float]:
        return r_stats(self.run_trades(bars))

    def fingerprint(self) -> str:
        """Chaîne qui identifie ce pipeline : paramètres + empreinte du code du signal et du filtre."""
        hs = self.half_spread_bp if np.ndim(self.half_spread_bp) == 0 else f"array{len(self.half_spread_bp)}"
        return (
            f"{self.name or 'pipeline'}|stop={self.stop_bp}|target={self.target_bp}|hold={self.max_hold}"
            f"|spread={self.spread_bp}|half={hs}|swapL={self.swap_long_bp}|swapS={self.swap_short_bp}"
            f"|slip={self.stop_slippage_bp}|signal={_fn_id(self.signal)}|filter={_fn_id(self.population_filter)}"
        )


def _t_one_sample(x: np.ndarray, mu: float) -> float:
    """t de Student de (x - mu) ; NaN si moins de 2 points ou variance nulle."""
    if len(x) < 2:
        return float("nan")
    sd = x.std(ddof=1)
    if not sd > 0:
        return float("nan")
    return float((x.mean() - mu) / (sd / np.sqrt(len(x))))


def t_threshold_bonferroni(alpha: float, n_tests: int) -> float:
    """Seuil unilatéral normal pour ``alpha`` famille-wise réparti sur ``n_tests`` (Bonferroni).

    Dérive la constante que les appels écrivaient en dur (3,6 ≈ alpha/n_tests de
    l'ordre de 1,6e-4). Approximation normale : valable pour n de trades grand.
    """
    if not (0 < alpha < 1) or n_tests < 1:
        raise ValueError("alpha dans ]0,1[ et n_tests >= 1")
    return float(NormalDist().inv_cdf(1.0 - alpha / n_tests))


@dataclass(frozen=True)
class NullReference:
    n_trades: int
    expected_r: float
    expected_r_se: float


def expected_r_under_null(
    pipeline: Pipeline,
    *,
    n_paths: int,
    n_bars: int,
    sigma_bp: float,
    seed: int,
    reference_filter: str = "none",
) -> NullReference:
    """R moyen de la MÉCANIQUE du pipeline sur marches à dérive nulle, sans compétence.

    Mêmes instants de décision (signal non nul), même simulation, mêmes coûts ;
    le sens est remplacé par un pile ou face indépendant des prix. Sous une
    martingale, tout écart à 0 de ce R est dû aux conventions d'exécution
    (péage, glissement, stop prioritaire, grille intra-barre), pas à un
    avantage : c'est le « zéro » correct du témoin (F-4).
    """
    if reference_filter not in ("none", "pipeline"):
        raise ValueError("reference_filter ∈ {'none', 'pipeline'}")
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), 7919]))
    all_r: list[float] = []
    for _ in range(n_paths):
        bars = random_walk_bars(n_bars, sigma_bp=sigma_bp, seed=int(rng.integers(2**31)))
        base = np.sign(np.asarray(pipeline.signal(bars)))
        coin = rng.choice(np.array([-1, 1]), size=len(bars))
        trades = pipeline.run_trades(bars, signal=base * coin, with_filter=(reference_filter == "pipeline"))
        all_r.extend(tr.r for tr in trades)
    r = np.asarray(all_r, dtype=float)
    if len(r) < 2:
        raise InconclusiveError("référence nulle sans trades : le pipeline ne trade pas sur du bruit")
    return NullReference(len(r), float(r.mean()), float(r.std(ddof=1) / np.sqrt(len(r))))


@dataclass(frozen=True)
class ControlResult:
    n_trades: int
    mean_r: float
    t: float  # t du R brut ; NE PAS l'utiliser comme critère (le péage le décale) — voir t_excess
    expected_r: float
    expected_r_se: float
    excess_r: float
    t_excess: float
    excess_r_filtered_ref: float
    t_excess_filtered_ref: float
    pipeline: str
    graine: int

    @property
    def conclusive(self) -> bool:
        return self.n_trades >= 2 and np.isfinite(self.t_excess)


def zero_drift_control(
    pipeline: Pipeline,
    *,
    n_paths: int,
    n_bars: int,
    sigma_bp: float,
    seed: int,
    n_ref_paths: int | None = None,
) -> ControlResult:
    """R moyen du pipeline sur ``n_paths`` marches sans dérive, et écart au R attendu.

    ``excess_r = mean_r - expected_r`` ; ``t_excess`` = t de Student de (R - expected_r)
    (R attendu traité comme constante ; son erreur-type est ``expected_r_se``, que
    ``n_ref_paths`` — par défaut 5 × n_paths — rend petite). Un résultat sans
    trade ou à variance nulle porte ``t_excess = NaN`` et ``conclusive = False`` :
    ce n'est pas un témoin à zéro, c'est l'absence de témoin.
    """
    rng = np.random.default_rng(seed)
    all_r: list[float] = []
    for _ in range(n_paths):
        bars = random_walk_bars(n_bars, sigma_bp=sigma_bp, seed=int(rng.integers(2**31)))
        all_r.extend(tr.r for tr in pipeline.run_trades(bars))
    r = np.asarray(all_r, dtype=float)
    n_ref = n_ref_paths if n_ref_paths is not None else 5 * n_paths
    if len(r) < 2:
        return ControlResult(len(r), float("nan"), float("nan"), float("nan"), float("nan"), float("nan"),
                             float("nan"), float("nan"), float("nan"), pipeline.fingerprint(), int(seed))
    ref = expected_r_under_null(pipeline, n_paths=n_ref, n_bars=n_bars, sigma_bp=sigma_bp, seed=seed)
    ref_f = (
        expected_r_under_null(pipeline, n_paths=n_ref, n_bars=n_bars, sigma_bp=sigma_bp, seed=seed,
                              reference_filter="pipeline")
        if pipeline.population_filter is not None
        else ref
    )
    return ControlResult(
        n_trades=len(r),
        mean_r=float(r.mean()),
        t=_t_one_sample(r, 0.0),
        expected_r=ref.expected_r,
        expected_r_se=ref.expected_r_se,
        excess_r=float(r.mean() - ref.expected_r),
        t_excess=_t_one_sample(r, ref.expected_r),
        excess_r_filtered_ref=float(r.mean() - ref_f.expected_r),
        t_excess_filtered_ref=_t_one_sample(r, ref_f.expected_r),
        pipeline=pipeline.fingerprint(),
        graine=int(seed),
    )


def write_temoin_json(
    path: str | Path,
    pipeline: Pipeline,
    *,
    n_paths: int,
    n_bars: int,
    sigma_bp: float,
    seed: int,
    min_trades: int = 500,
    n_ref_paths: int | None = None,
) -> dict:
    """Exécute le témoin et écrit ``temoin_derive_nulle.json`` au contrat fixé.

    Contrat : {"n_trades", "mean_r", "expected_r", "excess_r", "t_excess", "pipeline", "graine"}.
    Refuse d'écrire (``InconclusiveError``) si le témoin n'a rien mesuré :
    moins de ``min_trades`` trades, t NaN ou infini. Une pièce absente vaut
    mieux qu'une pièce qui s'ouvre sur du vide (F-3).
    """
    res = zero_drift_control(pipeline, n_paths=n_paths, n_bars=n_bars, sigma_bp=sigma_bp, seed=seed,
                             n_ref_paths=n_ref_paths)
    if res.n_trades < min_trades or not np.isfinite(res.t_excess):
        raise InconclusiveError(
            f"témoin inconcluant : n_trades={res.n_trades} (plancher {min_trades}), t_excess={res.t_excess}"
        )
    doc = {
        "n_trades": res.n_trades,
        "mean_r": res.mean_r,
        "expected_r": res.expected_r,
        "excess_r": res.excess_r,
        "t_excess": res.t_excess,
        "pipeline": res.pipeline,
        "graine": res.graine,
    }
    Path(path).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


def write_acausalite_json(
    path: str | Path,
    pipeline: Pipeline,
    bars: Bars,
    *,
    sigma_bp: float,
    seed: int,
    n_checks: int = 200,
    n_trade_checks: int = 50,
    n_noise_draws: int = 3,
    min_checked: int = 30,
) -> dict:
    """Exécute le détecteur sur le Pipeline et écrit ``acausalite.json`` au contrat fixé.

    Contrat : {"n_checked", "n_changed", "pipeline", "graine"}. ``n_checked`` et
    ``n_changed`` additionnent le contrôle des décisions (``detect_leak`` sur
    ``pipeline.decide``) et celui des trades (``detect_trade_leak`` sur la
    chaîne exécutée). Refuse d'écrire si l'un des deux a vérifié moins de
    ``min_checked`` instants (F-3).
    """
    from .acausality import detect_leak, detect_trade_leak

    a = detect_leak(pipeline, bars, sigma_bp=sigma_bp, seed=seed, n_checks=n_checks, n_noise_draws=n_noise_draws)
    b = detect_trade_leak(pipeline, bars, sigma_bp=sigma_bp, seed=seed + 1, n_checks=n_trade_checks,
                          n_noise_draws=max(1, n_noise_draws - 1))
    if a.n_checked < min_checked or b.n_checked < min(min_checked, n_trade_checks):
        raise InconclusiveError(
            f"détecteur inconcluant : décisions vérifiées={a.n_checked}, trades vérifiés={b.n_checked} "
            f"(plancher {min_checked})"
        )
    doc = {
        "n_checked": a.n_checked + b.n_checked,
        "n_changed": a.n_changed + b.n_changed,
        "pipeline": pipeline.fingerprint(),
        "graine": int(seed),
    }
    Path(path).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


# ---------------------------------------------------------------- puissance


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return float(max(0.0, centre - half)), float(min(1.0, centre + half))


@dataclass(frozen=True)
class PowerResult:
    edge_bp: float  # avantage nominal planté, par trade
    n_trades: int  # trades par répétition
    n_reps: int
    detection_probability: float
    ci_low: float  # Wilson 95 %
    ci_high: float
    realised_edge_bp: float  # mesuré : moyenne de sens × dérive plantée sur les barres de chaque trade
    mean_r: float  # moyenne, sur les répétitions, du R moyen
    expected_r: float
    mean_t_excess: float


def _plant_per_trade_drift(trades: list[Trade], n_bars: int, edge_bp: float) -> np.ndarray:
    """Dérive par barre (bp, signée) : edge_bp par trade, étalé sur les barres tenues, dans le sens du trade."""
    d = np.zeros(n_bars)
    for tr in trades:
        held = tr.exit_bar - tr.entry_bar + 1
        d[tr.entry_bar : tr.exit_bar + 1] += tr.direction * edge_bp / held
    return d


def power_curve(
    pipeline: Pipeline,
    *,
    edges_bp: Sequence[float],
    n_trades: int,
    n_reps: int,
    sigma_bp: float,
    seed: int,
    t_threshold: float,
    n_bars: int = 2_000,
    max_paths_per_rep: int = 200,
    n_ref_paths: int = 60,
) -> list[PowerResult]:
    """Probabilité de détecter un avantage planté par trade, pour ``n_trades`` trades.

    Pour chaque répétition (graine propre, indépendante des autres ; les mêmes
    répétitions servent à tous les avantages, tirages communs documentés) :
    1. des marches brutes de ``n_bars`` barres sont tirées jusqu'à obtenir
       ``n_trades`` trades ;
    2. première passe : le pipeline tourne sur la marche brute ; chaque trade
       reçoit ``edge_bp`` de rendement additionnel, étalé sur ses barres tenues,
       dans son sens ;
    3. deuxième passe : le MÊME bruit plus cette dérive ; le pipeline recalcule
       son signal et son filtre et tourne ; les ``n_trades`` premiers trades
       sont jugés ;
    4. détecté ⇔ t de (R - R attendu) > ``t_threshold``, R attendu calculé par
       ``expected_r_under_null`` (traité comme connu).
    L'avantage 0 donne le taux de faux positifs. La probabilité de détection
    est la part de répétitions détectées ; l'avantage réalisé est mesuré sur
    les trades de la deuxième passe (sens du trade × dérive plantée sur ses
    barres), car le pipeline peut ne pas retomber sur les positions de la première.
    """
    ref = expected_r_under_null(pipeline, n_paths=n_ref_paths, n_bars=n_bars, sigma_bp=sigma_bp, seed=seed)
    seeds = np.random.SeedSequence(int(seed)).spawn(n_reps)
    per_edge = {float(e): {"det": 0, "r": [], "t": [], "real": []} for e in edges_bp}
    for ss in seeds:
        rng = np.random.default_rng(ss)
        path_seeds: list[int] = []
        raws: list[Bars] = []
        pass1: list[list[Trade]] = []
        total = 0
        while total < int(np.ceil(1.2 * n_trades)):
            if len(raws) >= max_paths_per_rep:
                raise InconclusiveError(f"moins de {n_trades} trades après {max_paths_per_rep} chemins")
            s = int(rng.integers(2**31))
            bars = random_walk_bars(n_bars, sigma_bp=sigma_bp, seed=s)
            tr = pipeline.run_trades(bars)
            path_seeds.append(s)
            raws.append(bars)
            pass1.append(tr)
            total += len(tr)
        for e in edges_bp:
            rs: list[float] = []
            real: list[float] = []
            for s, raw, tr1 in zip(path_seeds, raws, pass1):
                d = _plant_per_trade_drift(tr1, n_bars, float(e))
                planted = random_walk_bars(n_bars, sigma_bp=sigma_bp, seed=s, drift_bp=d)
                tr2 = pipeline.run_trades(planted)
                rs.extend(t.r for t in tr2)
                real.extend(t.direction * d[t.entry_bar : t.exit_bar + 1].sum() for t in tr2)
            if len(rs) < n_trades:  # la deuxième passe peut perdre quelques trades : on complète pas, on signale
                raise InconclusiveError(f"deuxième passe: {len(rs)} trades < {n_trades}")
            r = np.asarray(rs[:n_trades], dtype=float)
            t = _t_one_sample(r, ref.expected_r)
            slot = per_edge[float(e)]
            slot["det"] += int(np.isfinite(t) and t > t_threshold)
            slot["r"].append(r.mean())
            slot["t"].append(t)
            slot["real"].append(float(np.mean(real[:n_trades])))
    out: list[PowerResult] = []
    for e in edges_bp:
        slot = per_edge[float(e)]
        lo, hi = _wilson(slot["det"], n_reps)
        out.append(
            PowerResult(
                edge_bp=float(e),
                n_trades=n_trades,
                n_reps=n_reps,
                detection_probability=slot["det"] / n_reps,
                ci_low=lo,
                ci_high=hi,
                realised_edge_bp=float(np.mean(slot["real"])),
                mean_r=float(np.mean(slot["r"])),
                expected_r=ref.expected_r,
                mean_t_excess=float(np.nanmean(slot["t"])),
            )
        )
    return out


def minimum_detectable_edge(results: Sequence[PowerResult], *, power: float = 0.8) -> float | None:
    """Plus petit avantage nominal détecté avec probabilité ≥ ``power`` ET tous les plus grands aussi.

    Exiger la monotonie évite de prendre un creux de bruit pour un seuil. None
    si aucun avantage essayé n'atteint ``power``.
    """
    ordered = sorted(results, key=lambda r: r.edge_bp)
    mde = None
    for r in reversed(ordered):
        if r.detection_probability >= power:
            mde = r.edge_bp
        else:
            break
    return mde
