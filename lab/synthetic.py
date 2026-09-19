"""Marche aléatoire à dérive nulle et avantage planté.

Unités : les distances sont en points de base (bp) du prix, 1 bp = 1e-4.
La dérive est nulle en rendement simple : E[close/open - 1] = 0 exactement.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

BP = 1e-4


@dataclass(frozen=True)
class Bars:
    """Barres OHLC. ``open[t+1] == close[t]`` (pas de gap)."""

    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray

    def __len__(self) -> int:
        return len(self.close)

    def slice(self, stop: int) -> "Bars":
        return Bars(self.open[:stop], self.high[:stop], self.low[:stop], self.close[:stop])

    @staticmethod
    def concat(a: "Bars", b: "Bars") -> "Bars":
        return Bars(
            np.concatenate([a.open, b.open]),
            np.concatenate([a.high, b.high]),
            np.concatenate([a.low, b.low]),
            np.concatenate([a.close, b.close]),
        )


def random_walk_bars(
    n_bars: int,
    *,
    sigma_bp: float,
    seed: int | np.random.Generator,
    start: float = 100.0,
    steps_per_bar: int = 20,
    drift_bp: np.ndarray | float = 0.0,
) -> Bars:
    """Barres construites par ``steps_per_bar`` pas de rendement simple gaussien.

    ``sigma_bp`` est l'écart-type du rendement d'une barre entière.
    ``drift_bp`` (scalaire ou tableau de taille ``n_bars``) est la dérive
    moyenne par barre ; 0 = témoin à dérive nulle.
    """
    rng = np.random.default_rng(seed)
    drift = np.broadcast_to(np.asarray(drift_bp, dtype=float), (n_bars,)) * BP
    step_sigma = sigma_bp * BP / np.sqrt(steps_per_bar)
    steps = rng.normal(0.0, step_sigma, size=(n_bars, steps_per_bar))
    steps += (drift / steps_per_bar)[:, None]
    # Chemin intra-barre en rendement simple cumulé, ancré sur l'ouverture.
    path = np.cumprod(1.0 + steps, axis=1)
    bar_close_factor = path[:, -1]
    opens = start * np.concatenate([[1.0], np.cumprod(bar_close_factor)[:-1]])
    highs = opens * np.maximum(1.0, path.max(axis=1))
    lows = opens * np.minimum(1.0, path.min(axis=1))
    closes = opens * bar_close_factor
    return Bars(opens, highs, lows, closes)


def plant_edge(bars: Bars, signal: np.ndarray, edge_bp: float) -> Bars:
    """Ajoute ``edge_bp`` de rendement moyen à la barre t+1 dans le sens de ``signal[t]``.

    ``signal[t]`` ∈ {-1, 0, +1} est la décision prise à la clôture de t.
    La barre t+1 est déformée après son ouverture (l'ouverture reste égale à la
    clôture de t) ; le niveau de prix décalé est conservé ensuite, comme le
    ferait une vraie dérive. Sert au test de puissance : un pipeline qui ne
    retrouve pas un avantage planté de x bp ne peut pas en détecter un réel.
    """
    signal = np.asarray(signal)
    if len(signal) != len(bars):
        raise ValueError("signal et bars doivent avoir la même longueur")
    shift = np.zeros(len(bars))
    shift[1:] = signal[:-1] * edge_bp * BP  # effet sur la barre suivante
    cumulative = np.cumprod(1.0 + shift)  # niveau cumulé, appliqué à partir de t+1
    prev_cum = np.concatenate([[1.0], cumulative[:-1]])
    opens = bars.open * prev_cum
    closes = bars.close * cumulative
    highs = np.maximum(bars.high * cumulative, opens)
    lows = np.minimum(bars.low * cumulative, opens)
    return Bars(opens, highs, lows, closes)


def continue_with_noise(bars: Bars, t: int, *, sigma_bp: float, seed: int | np.random.Generator) -> Bars:
    """Conserve les barres ``0..t`` inclus, remplace tout le reste par du bruit neuf.

    C'est l'opération de base du détecteur d'acausalité.
    """
    n_future = len(bars) - (t + 1)
    if n_future <= 0:
        return bars
    fresh = random_walk_bars(n_future, sigma_bp=sigma_bp, seed=seed, start=float(bars.close[t]))
    return Bars.concat(bars.slice(t + 1), fresh)
