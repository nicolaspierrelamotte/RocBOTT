"""Détecteur mécanique d'acausalité.

Pour une décision prise à l'instant t, remplacer toutes les données
postérieures à t par du bruit et recalculer. Si la décision (direction ou
appartenance à la population) change, il y a fuite du futur.

``decide(bars) -> np.ndarray`` renvoie, pour chaque barre t, la décision prise
à sa clôture : 0 = pas de trade, ±1 = trade conservé dans ce sens. Toute la
chaîne (signal + filtres de population) doit passer par cette fonction.
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


def detect_leak(
    decide: Decide,
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
    """
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
            if int(np.asarray(decide(alt))[t]) != int(base[t]):
                changed.append(t)
                break
    return LeakReport(len(picked), len(changed), changed)
