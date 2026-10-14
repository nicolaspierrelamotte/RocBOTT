"""Test de puissance : une probabilité de détection pour un nombre de trades donné (F-8, F-11).

L'avantage est planté PAR TRADE, dans le sens de la position, pendant qu'elle
est tenue (dérive), et jamais hors position. Aucune assertion de la forme
« est dans (a, b) » sans pouvoir d'échec : chaque assertion borne une probabilité
estimée par son intervalle de Wilson, ou compare deux estimations.
"""
from statistics import NormalDist

import numpy as np
import pytest

from lab.control import (
    Pipeline,
    PowerResult,
    minimum_detectable_edge,
    online_planted_path,
    power_curve,
    t_threshold_bonferroni,
)
from lab.simulate import simulate_trades
from lab.synthetic import bar_from_steps, draw_steps, random_walk_bars

SIGMA = 10.0
THRESHOLD = 3.6


def follow_last_bar(bars):
    return np.sign(bars.close - bars.open).astype(int)


def pipeline():
    return Pipeline(follow_last_bar, stop_bp=15, target_bp=15, max_hold=5)


def test_detection_probability_is_a_probability_over_many_draws_not_a_boolean():
    res = power_curve(pipeline(), edges_bp=[0, 4, 8], n_trades=150, n_reps=40, sigma_bp=SIGMA, seed=20,
                      t_threshold=THRESHOLD)
    p0, p4, p8 = res
    assert all(isinstance(r, PowerResult) and r.n_reps == 40 and r.n_trades == 150 for r in res)
    # faux positifs : l'avantage 0 n'est pas détecté (seuil 3,6 : de l'ordre de 2e-4 par répétition)
    assert p0.detection_probability <= 0.05 and p0.ci_high < 0.12, p0
    # un avantage de 8 bp par trade (réalisé ≈ 8) est détecté presque toujours à 150 trades
    assert p8.detection_probability >= 0.85 and p8.ci_low > 0.7, p8
    # 4 bp : franchement entre les deux, et la courbe est monotone
    assert p4.detection_probability < p8.detection_probability - 0.4, (p4, p8)
    assert p0.detection_probability <= p4.detection_probability <= p8.detection_probability
    # l'avantage réalisé est mesuré, et proche du nominal : « x bp » est bien un avantage PAR TRADE
    for r in (p4, p8):
        assert r.realised_edge_bp == pytest.approx(r.edge_bp, rel=0.1), r
    assert p0.realised_edge_bp == 0.0


def test_detection_probability_matches_the_normal_prediction_from_measured_quantities():
    """P(détection) ≈ Φ(E[t_excess] - seuil) : la probabilité estimée n'est pas libre."""
    r4 = power_curve(pipeline(), edges_bp=[5], n_trades=150, n_reps=60, sigma_bp=SIGMA, seed=21,
                     t_threshold=THRESHOLD)[0]
    predicted = NormalDist().cdf(r4.mean_t_excess - THRESHOLD)
    assert r4.ci_low - 0.06 <= predicted <= r4.ci_high + 0.06, (predicted, r4)
    assert 0.02 < r4.detection_probability < 0.98, r4  # ni 0 ni 1 : le test peut échouer des deux côtés


def test_power_grows_with_the_number_of_trades():
    few = power_curve(pipeline(), edges_bp=[4], n_trades=60, n_reps=30, sigma_bp=SIGMA, seed=22, t_threshold=THRESHOLD)[0]
    many = power_curve(pipeline(), edges_bp=[4], n_trades=450, n_reps=30, sigma_bp=SIGMA, seed=22, t_threshold=THRESHOLD)[0]
    assert many.detection_probability >= few.detection_probability + 0.3, (few, many)
    assert few.n_trades != many.n_trades


def test_minimum_detectable_edge_requires_monotone_power_at_target_level():
    def pr(e, p):
        return PowerResult(e, 100, 100, p, 0, 1, e, 0, 0, 0, 0)

    assert minimum_detectable_edge([pr(2, 0.1), pr(4, 0.5), pr(8, 0.85), pr(12, 0.99)]) == 8
    # un creux de bruit au-dessus du seuil ne fait pas un seuil
    assert minimum_detectable_edge([pr(2, 0.9), pr(4, 0.5), pr(8, 0.85)]) == 8
    assert minimum_detectable_edge([pr(2, 0.1), pr(4, 0.5)]) is None
    assert minimum_detectable_edge([pr(2, 0.1), pr(4, 0.79)], power=0.8) is None


def test_bonferroni_threshold_is_derived_not_asserted():
    # alpha famille 5 % sur 300 comparaisons (unilatéral) : ~3,6
    assert t_threshold_bonferroni(0.05, 300) == pytest.approx(3.6, abs=0.1)
    assert t_threshold_bonferroni(0.05, 1) == pytest.approx(1.645, abs=0.002)
    assert t_threshold_bonferroni(0.05, 10) > t_threshold_bonferroni(0.05, 2)
    with pytest.raises(ValueError):
        t_threshold_bonferroni(0.0, 3)


# ------------------------------------------------- la dérive planquée suit la position, pas le temps


def test_online_generation_without_edge_is_the_walk_and_the_simulation():
    steps = draw_steps(1_500, sigma_bp=SIGMA, seed=5)
    bars, trades, planted = online_planted_path(pipeline(), steps, drift_per_held_bar_bp=0.0)
    ref = random_walk_bars(1_500, sigma_bp=SIGMA, seed=5)
    for name in ("open", "high", "low", "close"):
        assert np.allclose(getattr(bars, name), getattr(ref, name), rtol=1e-12, atol=0), name
    offline = simulate_trades(ref, follow_last_bar(ref), stop_bp=15, target_bp=15, max_hold=5)
    assert [(t.decision_bar, t.entry_bar, t.exit_bar, t.direction) for t in trades] == [
        (t.decision_bar, t.entry_bar, t.exit_bar, t.direction) for t in offline
    ]
    assert np.allclose([t.r for t in trades], [t.r for t in offline])
    assert planted == [0.0] * len(trades)


def test_bar_from_steps_matches_random_walk_bars_with_drift():
    steps = draw_steps(50, sigma_bp=SIGMA, seed=6)
    drift = np.linspace(-3, 3, 50)
    ref = random_walk_bars(50, sigma_bp=SIGMA, seed=6, drift_bp=drift)
    price = 100.0
    for k in range(50):
        o, h, l, c = bar_from_steps(price, steps[k], drift[k])
        assert (o, h, l, c) == pytest.approx((ref.open[k], ref.high[k], ref.low[k], ref.close[k]), rel=1e-12)
        price = c


def test_edge_is_planted_only_while_in_position_and_in_its_direction():
    """Une dérive qui tombe hors position, ou à contresens, fausserait « par trade »."""
    steps = draw_steps(3_000, sigma_bp=SIGMA, seed=7)
    flat_bars, _, _ = online_planted_path(pipeline(), steps, drift_per_held_bar_bp=0.0)
    bars, trades, planted = online_planted_path(pipeline(), steps, drift_per_held_bar_bp=2.0)
    assert trades and len(planted) == len(trades)
    # avantage planté de chaque trade = dérive × barres tenues, dans le sens du trade
    assert all(p == pytest.approx(2.0 * (t.exit_bar - t.entry_bar + 1)) for p, t in zip(planted, trades))
    # avant le premier trade, les barres sont identiques à la marche sans avantage
    first = trades[0].entry_bar
    assert np.array_equal(bars.close[:first], flat_bars.close[:first])
    # la barre qui suit la sortie du dernier trade tenu n'a aucune dérive propre : même rendement qu'en l'absence d'avantage
    # sauf par le niveau de prix ; on compare donc les rendements de barre aux pas, hors des barres tenues
    held = np.zeros(3_000, dtype=bool)
    for t in trades:
        held[t.entry_bar : t.exit_bar + 1] = True
    ret_new = bars.close / bars.open - 1
    ret_flat = flat_bars.close / flat_bars.open - 1
    # même bruit : hors position et avant toute divergence de trades, le rendement est identique ; test sur la
    # première barre libre située après le premier trade (aucune autre décision n'a encore divergé là non plus)
    free_before_first = np.flatnonzero(~held[:first])
    assert np.allclose(ret_new[free_before_first], ret_flat[free_before_first], rtol=0, atol=1e-15)
    # dans le sens : le rendement moyen des barres tenues, signé par le sens, dépasse celui d'une marche sans dérive
    signed = np.concatenate([[t.direction * ret_new[k] for k in range(t.entry_bar, t.exit_bar + 1)] for t in trades])
    assert signed.mean() / 1e-4 > 1.0  # de l'ordre de 2 bp de dérive par barre tenue, bruit ≈ 0,1 bp
