import numpy as np

from lab.ftmo import barrier_probability, two_step_pass_probability


def test_no_edge_no_cost_matches_gambler_ruin():
    # Sans avantage : P(+10 avant -10) = 1/2, P(+5 avant -10) = 2/3 (relais §2).
    # Échantillon EXACTEMENT équilibré : un déséquilibre de 1,5 % des journées
    # (tirage au hasard de 4 000 jours) suffit à faire passer P de 0,50 à 0,62.
    daily = np.tile([-0.005, 0.005], 2000)
    r1 = barrier_probability(daily, target=0.10, max_loss=0.10, daily_loss=None, n_boot=3000, seed=1)
    r2 = barrier_probability(daily, target=0.05, max_loss=0.10, daily_loss=None, n_boot=3000, seed=2)
    assert abs(r1.p_target - 0.5) < 0.03
    assert abs(r2.p_target - 2 / 3) < 0.03
    assert r1.p_unfinished < 0.01  # plafond de 2 000 jours, queue de distribution


def test_daily_loss_rule_is_binding_and_two_step_multiplies():
    daily = np.array([0.02, -0.06, 0.01])
    r = barrier_probability(daily, target=0.10, max_loss=0.10, daily_loss=0.05, n_boot=500, seed=3)
    assert r.p_daily_loss > 0.9
    p, p1, p2 = two_step_pass_probability(np.full(50, 0.002), n_boot=50, seed=4)
    assert p1.p_target == 1.0 and p2.p_target == 1.0 and p == 1.0
    assert p1.median_days_to_target == 50 and p2.median_days_to_target == 25
