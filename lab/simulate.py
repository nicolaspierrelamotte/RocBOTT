"""Simulation de trades générique.

Décision à la clôture de la barre t, entrée à l'ouverture de t+1, une seule
position à la fois. Le stop et l'objectif sont des distances fixes en bp du
prix d'entrée. R = résultat / distance du stop (mesurée sur l'ouverture
médiane, sans coût).

Convention des coûts (F-7, à lire avant tout chiffre sur données réelles)

- Les barres fournies sont des barres MÉDIANES (mid). Les coûts sont ajoutés
  par la simulation.
- ``half_spread_bp`` : demi-écart bid/ask, en bp, à CHAQUE côté. Un achat se
  fait à l'ask (mid + h), une vente au bid (mid - h). Le stop et l'objectif
  d'une position longue se déclenchent sur le bid (donc sur ``low``/``high`` du
  mid, décalés de -h) ; ceux d'une position courte sur l'ask (décalés de +h).
  L'écart total payé sur un aller-retour est 2h. Scalaire ou tableau d'une
  valeur par barre (la valeur de la barre d'entrée sert à l'entrée, celle de
  la barre de sortie à la sortie).
- ``spread_bp`` : ancien péage scalaire, ÉCART COMPLET retiré une fois à la
  sortie, sans effet sur les déclenchements. Conservé pour compatibilité ; à
  éviter dès que ``half_spread_bp`` est connu.
- ``swap_long_bp`` / ``swap_short_bp`` : financement en bp du prix d'entrée,
  PAR BARRE TENUE (positif = coût, négatif = gain). Approximation : le vrai
  financement tombe au rollover (heure, mercredi triple), ce que des barres
  sans horodatage ne peuvent pas porter ; l'appelant fixe donc un coût par
  barre équivalent. Documenté, non vérifié sur données réelles.

Convention d'exécution (F-4)

- Un stop est soldé au PIRE du niveau et du prix d'ouverture de la barre
  (côté sortie) : si la barre ouvre au-delà du niveau (gap), le fill est
  l'ouverture. ``stop_slippage_bp`` ajoute un glissement explicite, adverse.
- Un objectif est soldé au niveau, jamais mieux (pas d'amélioration de prix
  sur gap : conservateur).
- Si une barre touche le stop et l'objectif, le stop l'emporte (conservateur).
- La grille intra-barre est inconnue de ``simulate_trades`` (OHLC seulement) :
  l'espérance de R sous dérive nulle n'est donc PAS supposée égale à -péage /
  stop ; elle se calcule par simulation (``lab.control.expected_r_under_null``).
- La décision prise à la clôture de la barre de sortie est sautée (la
  position est encore ouverte pendant cette barre) ; ne pas s'attendre à ce
  qu'une position sorte et ressorte sur la même clôture (F-28).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from .synthetic import BP, Bars

# Filtre de population : reçoit (bars, index de la barre d'entrée) et dit si
# le trade est conservé. Un filtre qui regarde bars[entry:] est acausal.
PopulationFilter = Callable[[Bars, int], bool]


@dataclass(frozen=True)
class Trade:
    decision_bar: int
    entry_bar: int
    exit_bar: int
    direction: int
    r: float


def decisions(bars: Bars, signal: np.ndarray, population_filter: PopulationFilter | None = None) -> np.ndarray:
    """Décision prise à la clôture de chaque barre, signal ET filtre composés.

    C'est l'UNIQUE endroit où le signal et le filtre de population se
    combinent : ``simulate_trades`` et ``Pipeline.decide`` l'appellent tous
    deux, donc ce que le détecteur d'acausalité voit est ce que la boucle de
    simulation exécute. Valeur 0 = pas de trade (signal nul, filtre qui écarte,
    ou dernière barre : sans barre suivante il n'y a pas d'entrée).
    """
    signal = np.asarray(signal)
    n = len(bars)
    if len(signal) != n:
        raise ValueError("signal et bars doivent avoir la même longueur")
    out = np.zeros(n, dtype=signal.dtype if signal.dtype.kind in "iuf" else float)
    for t in range(n - 1):
        s = signal[t]
        if s == 0:
            continue
        if population_filter is not None and not population_filter(bars, t + 1):
            continue
        out[t] = s
    return out


def _half(h: float | np.ndarray, k: int) -> float:
    return float(h[k]) if np.ndim(h) else float(h)


def simulate_trades(
    bars: Bars,
    signal: np.ndarray,
    *,
    stop_bp: float,
    target_bp: float,
    max_hold: int,
    spread_bp: float = 0.0,
    half_spread_bp: float | np.ndarray = 0.0,
    swap_long_bp: float = 0.0,
    swap_short_bp: float = 0.0,
    stop_slippage_bp: float = 0.0,
    population_filter: PopulationFilter | None = None,
) -> list[Trade]:
    decided = decisions(bars, signal, population_filter)
    n = len(bars)
    trades: list[Trade] = []
    t = 0
    while t < n - 1:
        s = int(np.sign(decided[t]))  # seul le signe compte pour la simulation
        if s == 0:
            t += 1
            continue
        entry = t + 1
        mid_open = bars.open[entry]
        h_in = _half(half_spread_bp, entry) * BP
        price = mid_open * (1.0 + s * h_in)  # fill d'entrée : ask si long, bid si court
        stop_dist = stop_bp * BP * mid_open
        target_dist = target_bp * BP * mid_open
        stop = price - s * stop_dist
        target = price + s * target_dist
        exit_bar = min(entry + max_hold - 1, n - 1)
        exit_price = None
        for k in range(entry, exit_bar + 1):
            h = _half(half_spread_bp, k) * BP
            side = 1.0 - s * h  # long : bid = mid(1-h) ; court : ask = mid(1+h)
            lo, hi, op = bars.low[k] * side, bars.high[k] * side, bars.open[k] * side
            hit_stop = lo <= stop if s > 0 else hi >= stop
            hit_target = hi >= target if s > 0 else lo <= target
            if hit_stop:
                # au pire du niveau et de l'ouverture (gap), plus glissement explicite
                level = min(stop, op) if s > 0 else max(stop, op)
                exit_price = level - s * stop_slippage_bp * BP * mid_open
                exit_bar = k
                break
            if hit_target:
                exit_price = target  # jamais mieux que le niveau
                exit_bar = k
                break
        if exit_price is None:
            h = _half(half_spread_bp, exit_bar) * BP
            exit_price = bars.close[exit_bar] * (1.0 - s * h)
        pnl = s * (exit_price - price)
        pnl -= spread_bp * BP * mid_open
        held = exit_bar - entry + 1
        swap = swap_long_bp if s > 0 else swap_short_bp
        pnl -= swap * BP * mid_open * held
        trades.append(Trade(t, entry, exit_bar, s, pnl / stop_dist))
        t = exit_bar + 1  # une position à la fois
    return trades


def r_stats(trades: list[Trade]) -> dict[str, float]:
    r = np.array([tr.r for tr in trades], dtype=float)
    if len(r) < 2:
        return {"n": float(len(r)), "mean_r": float(r.mean()) if len(r) else float("nan"), "t": float("nan")}
    sd = r.std(ddof=1)
    # sd nul : t indéterminé (NaN), pas +inf quel que soit le signe de la moyenne (F-26).
    t = r.mean() / (sd / np.sqrt(len(r))) if sd > 0 else float("nan")
    return {"n": float(len(r)), "mean_r": float(r.mean()), "t": float(t), "win_rate": float((r > 0).mean())}


def outside_bar_filter(bars: Bars, entry: int) -> bool:
    """Le filtre de Colibri : jette la barre externe d'entrée. ACAUSAL, pour test.

    Regarde la barre d'entrée elle-même, inconnue au moment de la décision.
    Ne pas importer hors des tests et du détecteur : il est exposé comme
    ``ACAUSAL_FILTERS`` pour que le laboratoire puisse refuser un pipeline qui
    l'emploie (F-27).
    """
    if entry == 0:
        return True
    return not (bars.high[entry] > bars.high[entry - 1] and bars.low[entry] < bars.low[entry - 1])


def causal_outside_bar_filter(bars: Bars, entry: int) -> bool:
    """Même règle appliquée à la barre de décision (déjà close) : causal."""
    d = entry - 1
    if d <= 0:
        return True
    return not (bars.high[d] > bars.high[d - 1] and bars.low[d] < bars.low[d - 1])


# Filtres connus pour regarder le futur : un Pipeline qui les emploie est refusé
# par ``Pipeline.assert_no_known_acausal_filter`` (garde, pas preuve : le détecteur reste juge).
ACAUSAL_FILTERS = (outside_bar_filter,)
