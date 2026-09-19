"""Reproduit le mode de défaillance de Colibri sur une marche à dérive nulle.

Signal : sens de la barre qui vient de clore (suivi naïf). Filtre : jeter les
trades dont la barre d'ENTRÉE est externe. Ce filtre regarde le futur ;
il doit fabriquer un R positif sur du bruit pur et être attrapé par le
détecteur. La même règle appliquée à la barre de décision est causale.
"""
import numpy as np

from lab.acausality import detect_leak
from lab.control import Pipeline, zero_drift_control
from lab.simulate import causal_outside_bar_filter, outside_bar_filter, simulate_trades
from lab.synthetic import random_walk_bars

SIGMA = 10.0


def follow_last_bar(bars):
    return np.sign(bars.close - bars.open).astype(int)


def make_pipeline(pop_filter):
    return Pipeline(follow_last_bar, stop_bp=15, target_bp=15, max_hold=5, population_filter=pop_filter)


def test_acausal_filter_fabricates_edge_on_pure_noise():
    leaky = zero_drift_control(make_pipeline(outside_bar_filter), n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=10)
    clean = zero_drift_control(make_pipeline(causal_outside_bar_filter), n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=10)
    none = zero_drift_control(make_pipeline(None), n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=10)
    assert leaky.t > 5, leaky          # le témoin à dérive nulle sonne
    assert abs(clean.t) < 3, clean     # la version causale reste à zéro
    assert abs(none.t) < 3, none


def test_detector_flags_acausal_filter_and_clears_causal_one():
    bars = random_walk_bars(5_000, sigma_bp=SIGMA, seed=11)

    def decide_leaky(b):
        s = follow_last_bar(b)
        keep = np.array([outside_bar_filter(b, t + 1) if t + 1 < len(b) else True for t in range(len(b))])
        return s * keep

    def decide_causal(b):
        s = follow_last_bar(b)
        keep = np.array([causal_outside_bar_filter(b, t + 1) if t + 1 < len(b) else True for t in range(len(b))])
        return s * keep

    leaky = detect_leak(decide_leaky, bars, sigma_bp=SIGMA, seed=12, n_checks=150)
    causal = detect_leak(decide_causal, bars, sigma_bp=SIGMA, seed=12, n_checks=150)
    assert leaky.leaks and leaky.leak_rate > 0.05, leaky
    assert not causal.leaks, causal


def test_spread_only_lowers_mean_r_by_spread_over_stop():
    p = Pipeline(follow_last_bar, stop_bp=20, target_bp=20, max_hold=5, spread_bp=1.0)
    res = zero_drift_control(p, n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=13)
    assert abs(res.excess_over_spread) < 3 * (1 / np.sqrt(res.n_trades))
    assert res.expected_r_from_spread == -0.05
