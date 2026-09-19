"""Témoin à dérive nulle et test de puissance par avantage planté.

Un *pipeline* est ici une paire :
- ``signal(bars) -> np.ndarray`` : ±1/0 à la clôture de chaque barre ;
- des paramètres de simulation (stop, objectif, durée, péage, filtre).

Le témoin à dérive nulle fait tourner le pipeline sur des marches aléatoires
sans dérive : le R moyen attendu est 0 (moins le péage). Un R significatif
est un bug du pipeline, jamais un avantage.

Le test de puissance plante un avantage de x bp dans le sens du signal du
pipeline lui-même, et vérifie que le pipeline le retrouve. Le plus petit x
retrouvé est le seuil de détection du laboratoire.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np

from .simulate import PopulationFilter, r_stats, simulate_trades
from .synthetic import Bars, plant_edge, random_walk_bars

Signal = Callable[[Bars], np.ndarray]


@dataclass(frozen=True)
class Pipeline:
    signal: Signal
    stop_bp: float
    target_bp: float
    max_hold: int
    spread_bp: float = 0.0
    population_filter: PopulationFilter | None = None

    def run(self, bars: Bars) -> dict[str, float]:
        trades = simulate_trades(
            bars,
            self.signal(bars),
            stop_bp=self.stop_bp,
            target_bp=self.target_bp,
            max_hold=self.max_hold,
            spread_bp=self.spread_bp,
            population_filter=self.population_filter,
        )
        return r_stats(trades)


@dataclass(frozen=True)
class ControlResult:
    n_trades: int
    mean_r: float
    t: float
    expected_r_from_spread: float

    @property
    def excess_over_spread(self) -> float:
        return self.mean_r - self.expected_r_from_spread


def zero_drift_control(
    pipeline: Pipeline,
    *,
    n_paths: int,
    n_bars: int,
    sigma_bp: float,
    seed: int,
) -> ControlResult:
    """R moyen du pipeline sur ``n_paths`` marches sans dérive."""
    rng = np.random.default_rng(seed)
    all_r: list[float] = []
    for _ in range(n_paths):
        bars = random_walk_bars(n_bars, sigma_bp=sigma_bp, seed=int(rng.integers(2**31)))
        trades = simulate_trades(
            bars,
            pipeline.signal(bars),
            stop_bp=pipeline.stop_bp,
            target_bp=pipeline.target_bp,
            max_hold=pipeline.max_hold,
            spread_bp=pipeline.spread_bp,
            population_filter=pipeline.population_filter,
        )
        all_r.extend(tr.r for tr in trades)
    r = np.asarray(all_r)
    sd = r.std(ddof=1) if len(r) > 1 else float("nan")
    t = r.mean() / (sd / np.sqrt(len(r))) if len(r) > 1 and sd > 0 else float("nan")
    return ControlResult(len(r), float(r.mean()), float(t), -pipeline.spread_bp / pipeline.stop_bp)


@dataclass(frozen=True)
class PowerResult:
    edge_bp: float
    n_trades: int
    mean_r: float
    t: float
    detected: bool


def power_test(
    pipeline: Pipeline,
    *,
    edges_bp: Sequence[float],
    n_paths: int,
    n_bars: int,
    sigma_bp: float,
    seed: int,
    t_threshold: float,
) -> list[PowerResult]:
    """Pour chaque avantage planté, le pipeline le retrouve-t-il (t > seuil) ?

    Le signal est calculé sur la marche brute, l'avantage est planté dans son
    sens, puis le pipeline tourne sur la marche déformée (il recalcule son
    signal, qui peut différer à la marge : c'est voulu, le pipeline ne voit
    jamais le signal « pur »). Le seuil ``t_threshold`` est celui du registre
    (Bonferroni sur le nombre de campagnes), pas 2.
    """
    results: list[PowerResult] = []
    for edge in edges_bp:
        rng = np.random.default_rng(seed)
        all_r: list[float] = []
        for _ in range(n_paths):
            raw = random_walk_bars(n_bars, sigma_bp=sigma_bp, seed=int(rng.integers(2**31)))
            planted = plant_edge(raw, pipeline.signal(raw), edge)
            trades = simulate_trades(
                planted,
                pipeline.signal(planted),
                stop_bp=pipeline.stop_bp,
                target_bp=pipeline.target_bp,
                max_hold=pipeline.max_hold,
                spread_bp=pipeline.spread_bp,
                population_filter=pipeline.population_filter,
            )
            all_r.extend(tr.r for tr in trades)
        r = np.asarray(all_r)
        sd = r.std(ddof=1) if len(r) > 1 else float("nan")
        t = r.mean() / (sd / np.sqrt(len(r))) if len(r) > 1 and sd > 0 else float("nan")
        results.append(PowerResult(edge, len(r), float(r.mean()), float(t), bool(t > t_threshold)))
    return results


def smallest_detected_edge(results: Sequence[PowerResult]) -> float | None:
    detected = [r.edge_bp for r in results if r.detected]
    return min(detected) if detected else None
