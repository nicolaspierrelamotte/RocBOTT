"""Exécution du simulateur : gaps, glissement, bid/ask, swap, zéro du témoin asymétrique.

F-4 (stop et objectif soldés au niveau, zéro du témoin faux dès stop ≠ objectif),
F-7 (coût bid/ask, swap), F-26 (t d'une série sans dispersion).
"""
import numpy as np
import pytest

from lab.control import Pipeline, expected_r_under_null, zero_drift_control
from lab.simulate import Trade, r_stats, simulate_trades
from lab.synthetic import BP, Bars


def flat_bars(n, price=100.0):
    a = np.full(n, price)
    return Bars(a.copy(), a.copy(), a.copy(), a.copy())


def bars_from(ohlc):
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*ohlc))
    return Bars(o, h, l, c)


def one_trade(bars, direction, **kw):
    sig = np.zeros(len(bars), dtype=int)
    sig[0] = direction
    kw.setdefault("stop_bp", 10)
    kw.setdefault("target_bp", 30)
    kw.setdefault("max_hold", 5)
    trades = simulate_trades(bars, sig, **kw)
    assert len(trades) == 1
    return trades[0]


# ---------------------------------------------------------------- F-4 : prix de sortie


def test_stop_on_a_gap_fills_at_the_open_not_at_the_level():
    # long à 100, stop à 99,90 ; la barre 2 ouvre à 99,50 (gap sous le stop)
    bars = bars_from([(100, 100, 100, 100), (100, 100.01, 99.99, 100), (99.5, 99.6, 99.4, 99.5)])
    tr = one_trade(bars, +1)
    assert tr.exit_bar == 2
    assert tr.r == pytest.approx((99.5 - 100.0) / (10 * BP * 100.0))  # -5 R, pas -1 R


def test_short_stop_on_a_gap_fills_at_the_open():
    bars = bars_from([(100, 100, 100, 100), (100, 100.01, 99.99, 100), (100.5, 100.6, 100.4, 100.5)])
    tr = one_trade(bars, -1)
    assert tr.r == pytest.approx(-5.0)


def test_target_is_never_filled_better_than_its_level_on_a_gap():
    bars = bars_from([(100, 100, 100, 100), (100, 100.01, 99.99, 100), (101, 101.2, 100.9, 101)])
    tr = one_trade(bars, +1)  # objectif à 100,30 ; la barre ouvre à 101
    assert tr.r == pytest.approx(30 / 10)


def test_stop_wins_when_a_bar_touches_both_levels():
    bars = bars_from([(100, 100, 100, 100), (100, 100.5, 99.5, 100)])
    assert one_trade(bars, +1).r == pytest.approx(-1.0)


def test_explicit_stop_slippage_is_adverse_for_both_directions():
    long_bars = bars_from([(100, 100, 100, 100), (100, 100, 99.8, 99.85)])
    short_bars = bars_from([(100, 100, 100, 100), (100, 100.2, 100, 100.15)])
    assert one_trade(long_bars, +1, stop_slippage_bp=2).r == pytest.approx(-1.2)
    assert one_trade(short_bars, -1, stop_slippage_bp=2).r == pytest.approx(-1.2)


# ---------------------------------------------------------------- F-4 : le zéro du témoin


def hashed_coin_signal(bars):
    """Sens pseudo-aléatoire indépendant des prix (fonction de l'indice seul) : aucune compétence."""
    idx = np.arange(len(bars), dtype=np.uint64)
    return np.where(((idx * np.uint64(2654435761)) >> np.uint64(7)) % np.uint64(2) == 0, 1, -1).astype(int)


@pytest.mark.parametrize("stop,target", [(10, 30), (30, 10)])
def test_asymmetric_stop_and_target_zero_drift_has_no_significant_excess(stop, target):
    """Stop ≠ objectif, dérive nulle : l'écart au R attendu n'est pas significatif.

    L'ancienne hypothèse « R attendu = -péage / stop » (= 0 ici) est fausse : le
    R brut s'en écarte de façon hautement significative, par la mécanique seule.
    """
    p = Pipeline(hashed_coin_signal, stop_bp=stop, target_bp=target, max_hold=5)
    res = zero_drift_control(p, n_paths=20, n_bars=5_000, sigma_bp=10.0, seed=31)
    assert res.n_trades > 20_000
    assert abs(res.t_excess) < 3, res
    assert abs(res.t) > 4, (res, "le zéro naïf est faux: la mécanique décale le R brut")
    assert abs(res.expected_r) > 0.02, res


def test_expected_r_with_spread_is_computed_not_assumed():
    p = Pipeline(hashed_coin_signal, stop_bp=20, target_bp=20, max_hold=5, half_spread_bp=0.5)
    ref = expected_r_under_null(p, n_paths=30, n_bars=5_000, sigma_bp=10.0, seed=32)
    assert ref.expected_r == pytest.approx(-0.05, abs=0.012)  # 1 bp de péage total / 20 bp de stop
    assert ref.mean_hold > 1


# ---------------------------------------------------------------- F-7 : bid/ask et swap


def test_half_spread_total_cost_equals_full_spread_when_no_trigger():
    bars = flat_bars(6)
    both = one_trade(bars, +1, half_spread_bp=1.0)
    legacy = one_trade(bars, +1, spread_bp=2.0)
    assert both.r == pytest.approx(legacy.r) == pytest.approx(-2.0 * BP * 100.0 / (10 * BP * 100.0))


def test_short_stop_triggers_on_the_ask_side():
    """Une vente se déclenche sur l'ask : le haut du mid + demi-écart touche un stop que le mid ne touche pas."""
    bars = bars_from([(100, 100, 100, 100), (100, 100.085, 100, 100.0), (100, 100, 100, 100)])
    assert one_trade(bars, -1, spread_bp=2.0).r == pytest.approx(-0.2)  # ancien péage : pas déclenché
    assert one_trade(bars, -1, half_spread_bp=1.0).exit_bar == 1       # bid/ask : stoppé dans la barre 1
    assert one_trade(bars, -1, half_spread_bp=1.0).r == pytest.approx(-1.0)


def test_long_target_needs_the_bid_to_reach_it():
    # objectif à 100,10 + 0,01 (entrée à l'ask) = 100,11 sur le bid ; le mid haut 100,115 -> bid 100,105 < 100,11
    bars = bars_from([(100, 100, 100, 100), (100, 100.115, 100, 100.0), (100, 100, 100, 100)])
    tr = one_trade(bars, +1, stop_bp=10, target_bp=10, half_spread_bp=1.0)
    assert tr.exit_bar != 1
    assert one_trade(bars, +1, stop_bp=10, target_bp=10).exit_bar == 1  # sans écart, le mid l'aurait atteint


def test_swap_is_charged_per_bar_held_and_is_signed_per_direction():
    bars = flat_bars(8)
    base = one_trade(bars, +1).r
    long_cost = one_trade(bars, +1, swap_long_bp=0.5).r
    assert long_cost - base == pytest.approx(-(0.5 * 5) / 10)  # 5 barres tenues, 0,5 bp / barre, stop 10 bp
    short_gain = one_trade(bars, -1, swap_short_bp=-0.5).r - one_trade(bars, -1).r
    assert short_gain == pytest.approx(+(0.5 * 5) / 10)


def test_half_spread_accepts_one_value_per_bar():
    bars = flat_bars(6)
    h = np.zeros(6)
    h[1] = 1.0  # large à l'entrée, nul à la sortie
    tr = one_trade(bars, +1, half_spread_bp=h)
    assert tr.r == pytest.approx(-1.0 * BP * 100 / (10 * BP * 100))  # seul le demi-écart d'entrée est payé


# ---------------------------------------------------------------- F-26 : t d'une série sans dispersion


def test_r_stats_zero_dispersion_gives_nan_t_whatever_the_sign():
    for r in (+0.5, -0.5):
        stats = r_stats([Trade(0, 1, 2, 1, r) for _ in range(5)])
        assert np.isnan(stats["t"]), stats
