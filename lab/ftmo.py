"""Critère de jugement commun (relais §2, spec Z-26).

Probabilité d'atteindre la cible avant la perte maximale statique ou la perte
journalière, par rééchantillonnage des journées. Le Sharpe ne suffit pas.

Règles FTMO 2-Step vérifiées le 19/09/2026 : phase 1 +10 %, phase 2 +5 %,
perte maximale 10 % statique, perte journalière 5 % positions comprises.
Ces valeurs sont des arguments, jamais des constantes cachées.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BarrierResult:
    p_target: float
    p_max_loss: float
    p_daily_loss: float
    p_unfinished: float
    median_days_to_target: float


def barrier_probability(
    daily_returns: np.ndarray,
    *,
    target: float,
    max_loss: float,
    daily_loss: float | None,
    n_boot: int,
    seed: int,
    max_days: int = 2000,
    block: int = 1,
) -> BarrierResult:
    """Rééchantillonne les journées (par blocs de ``block``) et joue le défi.

    ``daily_returns`` en fraction du capital initial (0,01 = +1 %). La perte
    maximale est statique (mesurée depuis le capital initial). La perte
    journalière compare une journée à son ouverture ; ``None`` la désactive.
    """
    rng = np.random.default_rng(seed)
    r = np.asarray(daily_returns, dtype=float)
    if len(r) == 0:
        raise ValueError("aucune journée")
    outcomes = {"target": 0, "max_loss": 0, "daily_loss": 0, "unfinished": 0}
    days_to_target: list[int] = []
    n_blocks = int(np.ceil(max_days / block))
    for _ in range(n_boot):
        starts = rng.integers(0, len(r), size=n_blocks)
        idx = (starts[:, None] + np.arange(block)[None, :]).ravel() % len(r)
        path = r[idx][:max_days]
        equity = 1.0
        result = "unfinished"
        for d, x in enumerate(path, start=1):
            if daily_loss is not None and x <= -daily_loss:
                result = "daily_loss"
                break
            equity += x
            if equity <= 1.0 - max_loss:
                result = "max_loss"
                break
            if equity >= 1.0 + target:
                result = "target"
                days_to_target.append(d)
                break
        outcomes[result] += 1
    return BarrierResult(
        outcomes["target"] / n_boot,
        outcomes["max_loss"] / n_boot,
        outcomes["daily_loss"] / n_boot,
        outcomes["unfinished"] / n_boot,
        float(np.median(days_to_target)) if days_to_target else float("nan"),
    )


def two_step_pass_probability(
    daily_returns: np.ndarray,
    *,
    phase1_target: float = 0.10,
    phase2_target: float = 0.05,
    max_loss: float = 0.10,
    daily_loss: float | None = 0.05,
    n_boot: int = 2000,
    seed: int = 0,
    **kwargs,
) -> tuple[float, BarrierResult, BarrierResult]:
    """Probabilité de passer les deux phases, supposées indépendantes."""
    p1 = barrier_probability(daily_returns, target=phase1_target, max_loss=max_loss, daily_loss=daily_loss, n_boot=n_boot, seed=seed, **kwargs)
    p2 = barrier_probability(daily_returns, target=phase2_target, max_loss=max_loss, daily_loss=daily_loss, n_boot=n_boot, seed=seed + 1, **kwargs)
    return p1.p_target * p2.p_target, p1, p2
