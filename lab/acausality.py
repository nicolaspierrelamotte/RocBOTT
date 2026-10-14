"""Détecteur mécanique d'acausalité.

Pour une décision prise à l'instant t, remplacer toutes les données
postérieures à t par du bruit et recalculer. Si la décision (direction ou
appartenance à la population) change, il y a fuite du futur.

Deux entrées possibles (F-2) :

- un ``Pipeline`` (``lab.control.Pipeline``) : le détecteur appelle
  ``pipeline.decide(bars)``, qui compose le signal ET le filtre de population
  par la même fonction (``lab.simulate.decisions``) que celle de
  ``simulate_trades``. Aucune ``decide`` à recopier à la main. C'est l'entrée à
  utiliser pour toute mesure.
- un appelable ``decide(bars) -> np.ndarray`` (une décision par barre : 0 = pas
  de trade, ±1 = trade). Garde pour les cas hors Pipeline ; ce qu'il certifie
  est ce qu'on lui tend, rien de plus.

``detect_trade_leak`` rejoue de plus la liste des trades produite par
``simulate_trades`` telle qu'elle tourne (boucle comprise) : les trades dont
la décision est ≤ t ne doivent pas changer quand le futur de t est du bruit.

LIMITE CONNUE, non levée : seules les barres (``bars``) sont remplacées. Une
donnée lue hors de l'argument ``bars`` (tableau précalculé avec un décalage
vers l'avenir, autre instrument, paramètres estimés sur tout l'échantillon)
n'est jamais perturbée ; le détecteur renvoie alors « pas de fuite » à tort.
Un pipeline qui lit autre chose que ``bars`` ne peut pas être certifié par ce
module (voir ``reponses_lot_A.md``, F-2).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from .synthetic import Bars, continue_with_noise

Decide = Callable[[Bars], np.ndarray]


@dataclass
class LeakReport:
    n_checked: int
    n_changed: int
    changed_at: list[int] = field(default_factory=list)

    @property
    def leak_rate(self) -> float:
        return self.n_changed / self.n_checked if self.n_checked else 0.0

    @property
    def leaks(self) -> bool:
        return self.n_changed > 0

    @property
    def conclusive(self) -> bool:
        """Faux si rien n'a été vérifié : « pas de fuite » n'est alors pas une mesure."""
        return self.n_checked > 0


def _as_decide(obj) -> Decide:
    """Accepte un Pipeline (méthode ``decide``) ou un appelable ``decide``."""
    if hasattr(obj, "decide") and callable(obj.decide):
        return obj.decide
    if callable(obj):
        return obj
    raise TypeError("detect_leak attend un Pipeline ou un appelable decide(bars)")


def detect_leak(
    decide_or_pipeline,
    bars: Bars,
    *,
    sigma_bp: float,
    seed: int,
    n_checks: int = 200,
    n_noise_draws: int = 3,
    only_where_decided: bool = True,
) -> LeakReport:
    """Rejoue ``n_checks`` instants t avec ``n_noise_draws`` futurs différents chacun.

    ``only_where_decided`` : ne teste que les t où la décision d'origine est
    non nulle (c'est là qu'un filtre de population peut avoir menti) ; sinon
    échantillonne uniformément.
    Les décisions sont comparées sans conversion en entier (F-18) : une
    décision fractionnaire qui change est une fuite.
    """
    decide = _as_decide(decide_or_pipeline)
    rng = np.random.default_rng(seed)
    base = np.asarray(decide(bars))
    if len(base) != len(bars):
        raise ValueError("decide doit renvoyer une décision par barre")
    candidates = np.flatnonzero(base != 0) if only_where_decided else np.arange(len(bars) - 1)
    candidates = candidates[candidates < len(bars) - 1]
    if len(candidates) == 0:
        return LeakReport(0, 0)
    picked = rng.choice(candidates, size=min(n_checks, len(candidates)), replace=False)
    changed: list[int] = []
    for t in sorted(int(x) for x in picked):
        for _ in range(n_noise_draws):
            alt = continue_with_noise(bars, t, sigma_bp=sigma_bp, seed=int(rng.integers(2**31)))
            if float(np.asarray(decide(alt))[t]) != float(base[t]):
                changed.append(t)
                break
    return LeakReport(len(picked), len(changed), changed)


def detect_trade_leak(
    pipeline,
    bars: Bars,
    *,
    sigma_bp: float,
    seed: int,
    n_checks: int = 100,
    n_noise_draws: int = 2,
) -> LeakReport:
    """Même épreuve, mais sur les TRADES que ``simulate_trades`` produit.

    Pour un t choisi parmi les barres de décision des trades, on remplace le
    futur de t par du bruit, on relance toute la chaîne (signal, filtre,
    boucle de simulation) et on compare les trades dont ``decision_bar <= t`` :
    (barre de décision, barre d'entrée, sens) doivent être identiques. La sortie
    et le R de ces trades dépendent légitimement du futur et ne sont pas
    comparés. Exige un objet avec ``run_trades(bars)``.
    """
    rng = np.random.default_rng(seed)

    def head(trades, t):
        return [(tr.decision_bar, tr.entry_bar, tr.direction) for tr in trades if tr.decision_bar <= t]

    base = pipeline.run_trades(bars)
    candidates = np.array([tr.decision_bar for tr in base if tr.decision_bar < len(bars) - 1], dtype=int)
    if len(candidates) == 0:
        return LeakReport(0, 0)
    picked = rng.choice(candidates, size=min(n_checks, len(candidates)), replace=False)
    changed: list[int] = []
    for t in sorted(int(x) for x in picked):
        ref = head(base, t)
        for _ in range(n_noise_draws):
            alt = continue_with_noise(bars, t, sigma_bp=sigma_bp, seed=int(rng.integers(2**31)))
            if head(pipeline.run_trades(alt), t) != ref:
                changed.append(t)
                break
    return LeakReport(len(picked), len(changed), changed)
