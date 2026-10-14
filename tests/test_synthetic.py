import numpy as np
import pytest

from lab.synthetic import BP, Bars, continue_with_noise, plant_edge, random_walk_bars


def test_zero_drift_walk_has_zero_mean_return_and_consistent_ohlc():
    bars = random_walk_bars(50_000, sigma_bp=10, seed=1)
    ret = bars.close / bars.open - 1
    assert abs(ret.mean()) < 3 * ret.std() / np.sqrt(len(ret))
    assert np.allclose(bars.open[1:], bars.close[:-1])
    assert (bars.high >= np.maximum(bars.open, bars.close)).all()
    assert (bars.low <= np.minimum(bars.open, bars.close)).all()
    assert abs(ret.std() / BP - 10) < 0.3


def _random_signal(n, seed):
    return np.random.default_rng(seed).choice([-1, 0, 1], size=n)


def _check_plant_edge_is_next_bar_only(plant, n=20_000, edge=5.0, seed=2):
    """Contrat de ``plant_edge`` (F-15) : sur un signal ±1/0 NON constant,

    1. le rendement de la barre t+1 est décalé de ``edge × signal[t]`` (au facteur exact 1+r près) ;
    2. la barre 0 et les barres dont la veille n'a pas de signal ne sont pas touchées ;
    3. changer ``signal[j]`` seul ne change que la barre j+1 (pas la barre j, pas j+2).
    Écarts mesurés à la précision machine : le terme du second ordre est exactement r × edge (formule
    fermée ci-dessous), pas une tolérance « à l'œil ».
    """
    bars = random_walk_bars(n, sigma_bp=10, seed=seed)
    signal = _random_signal(n, seed + 100)
    planted = plant(bars, signal, edge)
    ret_raw = bars.close / bars.open - 1
    ret_new = planted.close / planted.open - 1
    expected = np.zeros(n)
    expected[1:] = signal[:-1] * edge * BP * (1 + ret_raw[1:])
    assert np.allclose(ret_new - ret_raw, expected, rtol=0, atol=1e-12)
    assert (planted.high >= np.maximum(planted.open, planted.close)).all()
    assert (planted.low <= np.minimum(planted.open, planted.close)).all()
    # indépendance de la barre t vis-à-vis de signal[t]
    j = int(np.flatnonzero(signal == 0)[10])
    flipped = signal.copy()
    flipped[j] = 1
    other = plant(bars, flipped, edge)
    ret_other = other.close / other.open - 1
    changed = np.flatnonzero(~np.isclose(ret_other, ret_new, rtol=0, atol=1e-12))
    assert changed.tolist() == [j + 1]


def test_plant_edge_shifts_next_bar_return_only():
    _check_plant_edge_is_next_bar_only(plant_edge)


def test_the_plant_edge_test_would_catch_a_one_bar_shift():
    """Test du test : un décalage signal[t+1] (fuite) ou signal[t] (même barre) est refusé par le même contrôle."""

    def leaky_plant(bars, signal, edge_bp):
        shifted = np.concatenate([signal[1:], [0]])  # barre t+1 avantagée par signal[t+1] : fuite
        return plant_edge(bars, shifted, edge_bp)

    def same_bar_plant(bars, signal, edge_bp):
        shift = np.concatenate([[0], signal[:-1]])  # signal[t-1] sur la barre t+1
        return plant_edge(bars, shift, edge_bp)

    with pytest.raises(AssertionError):
        _check_plant_edge_is_next_bar_only(leaky_plant)
    with pytest.raises(AssertionError):
        _check_plant_edge_is_next_bar_only(same_bar_plant)


def test_plant_edge_second_order_term_is_the_documented_one():
    # Terme du second ordre r × e : jusqu'à ~4σ × e = 40 bp × 5 bp = 0,02 bp pour des barres extrêmes
    # (pas 0,005 bp comme l'ancien commentaire, qui prenait σ au lieu de 4σ).
    bars = random_walk_bars(20_000, sigma_bp=10, seed=2)
    planted = plant_edge(bars, np.ones(len(bars), dtype=int), 5)
    diff = ((planted.close / planted.open - 1) - (bars.close / bars.open - 1)) / BP
    r = (bars.close / bars.open - 1)[1:]
    assert np.allclose(diff[1:], 5 * (1 + r), rtol=0, atol=1e-8)
    assert 0.015 < np.abs(diff[1:] - 5).max() < 0.05


def test_continue_with_noise_keeps_past_and_replaces_future():
    bars = random_walk_bars(100, sigma_bp=10, seed=3)
    alt = continue_with_noise(bars, 40, sigma_bp=10, seed=99)
    assert len(alt) == len(bars)
    assert np.array_equal(alt.close[:41], bars.close[:41])
    assert alt.open[41] == bars.close[40]
    assert not np.array_equal(alt.close[41:], bars.close[41:])
