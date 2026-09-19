import numpy as np

from lab.synthetic import BP, Bars, continue_with_noise, plant_edge, random_walk_bars


def test_zero_drift_walk_has_zero_mean_return_and_consistent_ohlc():
    bars = random_walk_bars(50_000, sigma_bp=10, seed=1)
    ret = bars.close / bars.open - 1
    assert abs(ret.mean()) < 3 * ret.std() / np.sqrt(len(ret))
    assert np.allclose(bars.open[1:], bars.close[:-1])
    assert (bars.high >= np.maximum(bars.open, bars.close)).all()
    assert (bars.low <= np.minimum(bars.open, bars.close)).all()
    assert abs(ret.std() / BP - 10) < 0.3


def test_plant_edge_shifts_next_bar_return_only():
    bars = random_walk_bars(20_000, sigma_bp=10, seed=2)
    signal = np.ones(len(bars), dtype=int)
    planted = plant_edge(bars, signal, edge_bp=5)
    ret_raw = bars.close / bars.open - 1
    ret_new = planted.close / planted.open - 1
    diff = (ret_new - ret_raw) / BP
    assert diff[0] == 0
    # Terme du second ordre r*e : au plus sigma*edge = 10 bp * 5 bp = 0,005 bp.
    assert np.allclose(diff[1:], 5.0, atol=0.05)
    assert abs(diff[1:].mean() - 5.0) < 1e-3
    assert (planted.high >= np.maximum(planted.open, planted.close)).all()
    assert (planted.low <= np.minimum(planted.open, planted.close)).all()


def test_continue_with_noise_keeps_past_and_replaces_future():
    bars = random_walk_bars(100, sigma_bp=10, seed=3)
    alt = continue_with_noise(bars, 40, sigma_bp=10, seed=99)
    assert len(alt) == len(bars)
    assert np.array_equal(alt.close[:41], bars.close[:41])
    assert alt.open[41] == bars.close[40]
    assert not np.array_equal(alt.close[41:], bars.close[41:])
