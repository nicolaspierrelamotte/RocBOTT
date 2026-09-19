"""Simulation de trades générique.

Décision à la clôture de la barre t, entrée à l'ouverture de t+1, une seule
position à la fois. Le stop et l'objectif sont des distances fixes en bp.
Si une barre touche le stop et l'objectif, le stop l'emporte (conservateur).
R = résultat / distance du stop. Le péage (``spread_bp``) est retiré une fois
par trade.
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


def simulate_trades(
    bars: Bars,
    signal: np.ndarray,
    *,
    stop_bp: float,
    target_bp: float,
    max_hold: int,
    spread_bp: float = 0.0,
    population_filter: PopulationFilter | None = None,
) -> list[Trade]:
    signal = np.asarray(signal)
    n = len(bars)
    trades: list[Trade] = []
    t = 0
    while t < n - 1:
        s = int(signal[t])
        entry = t + 1
        if s == 0 or (population_filter is not None and not population_filter(bars, entry)):
            t += 1
            continue
        price = bars.open[entry]
        stop_dist = stop_bp * BP * price
        target_dist = target_bp * BP * price
        stop = price - s * stop_dist
        target = price + s * target_dist
        exit_bar = min(entry + max_hold - 1, n - 1)
        pnl = None
        for k in range(entry, exit_bar + 1):
            hit_stop = bars.low[k] <= stop if s > 0 else bars.high[k] >= stop
            hit_target = bars.high[k] >= target if s > 0 else bars.low[k] <= target
            if hit_stop:
                pnl, exit_bar = -stop_dist, k
                break
            if hit_target:
                pnl, exit_bar = target_dist, k
                break
        if pnl is None:
            pnl = s * (bars.close[exit_bar] - price)
        pnl -= spread_bp * BP * price
        trades.append(Trade(t, entry, exit_bar, s, pnl / stop_dist))
        t = exit_bar + 1  # une position à la fois
    return trades


def r_stats(trades: list[Trade]) -> dict[str, float]:
    r = np.array([tr.r for tr in trades], dtype=float)
    if len(r) < 2:
        return {"n": float(len(r)), "mean_r": float(r.mean()) if len(r) else float("nan"), "t": float("nan")}
    sd = r.std(ddof=1)
    t = r.mean() / (sd / np.sqrt(len(r))) if sd > 0 else float("inf")
    return {"n": float(len(r)), "mean_r": float(r.mean()), "t": float(t), "win_rate": float((r > 0).mean())}


def outside_bar_filter(bars: Bars, entry: int) -> bool:
    """Le filtre de Colibri : jette la barre externe d'entrée. ACAUSAL, pour test.

    Regarde la barre d'entrée elle-même, inconnue au moment de la décision.
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
