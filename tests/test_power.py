import numpy as np

from lab.control import Pipeline, power_test, smallest_detected_edge


def follow_last_bar(bars):
    return np.sign(bars.close - bars.open).astype(int)


def test_power_test_finds_large_edge_not_zero():
    p = Pipeline(follow_last_bar, stop_bp=15, target_bp=15, max_hold=5)
    res = power_test(p, edges_bp=[0, 2, 10], n_paths=20, n_bars=5_000, sigma_bp=10, seed=20, t_threshold=3.6)
    by_edge = {r.edge_bp: r for r in res}
    assert not by_edge[0].detected, by_edge[0]
    assert by_edge[10].detected, by_edge[10]
    assert by_edge[10].mean_r > by_edge[2].mean_r > by_edge[0].mean_r - 0.02
    assert smallest_detected_edge(res) in (2, 10)
