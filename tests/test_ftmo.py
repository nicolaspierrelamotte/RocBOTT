import numpy as np
import pytest

from lab.ftmo import RULES_VERIFIED_ON, barrier_probability, two_step_pass_probability


def _symmetric_continuous_sample(seed=0, n=2000, scale=0.006):
    """Échantillon continu et asymétrique de forme, mais de moyenne EXACTEMENT nulle (centré, pas bricolé après échec)."""
    rng = np.random.default_rng(seed)
    x = rng.exponential(scale, size=n) - rng.exponential(scale * 0.5, size=n)  # forme biaisée, ni symétrique ni à deux valeurs
    return x - x.mean()


def test_no_edge_no_cost_matches_gambler_ruin_on_a_centred_continuous_sample():
    # Sans avantage : P(+10 avant -10) = 1/2, P(+5 avant -10) = 2/3 (relais §2).
    # Échantillon centré (moyenne exactement nulle) mais continu et de forme biaisée : on ne triche pas
    # avec une loi à deux valeurs équilibrée à la main. Le rééchantillonnage reste i.i.d.
    daily = _symmetric_continuous_sample()
    assert abs(daily.mean()) < 1e-15 and daily.std() > 0.002 and abs(((daily - daily.mean()) ** 3).mean()) > 0
    r1 = barrier_probability(daily, target=0.10, max_loss=0.10, daily_loss=None, n_boot=3000, seed=1)
    r2 = barrier_probability(daily, target=0.05, max_loss=0.10, daily_loss=None, n_boot=3000, seed=2)
    assert abs(r1.p_target - 0.5) < 0.04
    assert abs(r2.p_target - 2 / 3) < 0.04
    assert r1.p_unfinished < 0.01  # plafond de 2 000 jours, queue de distribution
    assert r1.equity_basis == "close_only"


def test_daily_loss_rule_is_binding():
    daily = np.array([0.02, -0.06, 0.01])
    r = barrier_probability(daily, target=0.10, max_loss=0.10, daily_loss=0.05, n_boot=500, seed=3)
    assert r.p_daily_loss > 0.9


def test_two_step_probability_is_the_product_of_two_non_trivial_phase_probabilities():
    daily = _symmetric_continuous_sample(seed=3)
    p, p1, p2 = two_step_pass_probability(daily, n_boot=800, seed=4, daily_loss=None)
    assert 0.2 < p1.p_target < 0.8 and 0.4 < p2.p_target < 0.95  # ni 0 ni 1 : le produit est exercé
    assert p1.p_target != p2.p_target
    assert p == pytest.approx(p1.p_target * p2.p_target)
    assert p < min(p1.p_target, p2.p_target)
    # cas déterministe conservé : la médiane des jours vers la cible suit la cible
    _, d1, d2 = two_step_pass_probability(np.full(50, 0.002), n_boot=50, seed=4)
    assert d1.median_days_to_target == 50 and d2.median_days_to_target == 25


def test_daily_loss_default_rules_are_applied_in_two_step_and_dated():
    daily = _symmetric_continuous_sample(seed=3)
    daily[:20] = -0.06  # 20 jours à -6 % : la règle des 5 % doit mordre dans les deux phases
    with_rule, _, _ = two_step_pass_probability(daily, n_boot=300, seed=5)
    without_rule, _, _ = two_step_pass_probability(daily, n_boot=300, seed=5, daily_loss=None)
    assert with_rule < without_rule
    assert RULES_VERIFIED_ON == "2026-09-19"


def test_block_resampling_keeps_clusters_that_iid_resampling_destroys():
    # 190 jours à +0,4 % et une grappe de 8 jours à -2 % (-16 % d'un trait). Tirés un à un, la grappe disparaît ;
    # par blocs de 8, elle est tirée en entier avec probabilité 1/200 par bloc : la ruine devient possible.
    r = np.full(200, 0.004)
    r[50:58] = -0.02
    iid = barrier_probability(r, target=0.10, max_loss=0.10, daily_loss=None, n_boot=1500, seed=1, max_days=400, block=1)
    blk = barrier_probability(r, target=0.10, max_loss=0.10, daily_loss=None, n_boot=1500, seed=1, max_days=400, block=8)
    assert iid.p_max_loss < 0.01
    assert blk.p_max_loss > 0.03


# ----------------------------------------------------------- F-12 : équité intra-journalière


def test_a_day_closing_at_minus_3_but_touching_minus_6_fails_the_5_percent_rule():
    daily = np.array([-0.03, 0.02, -0.03])
    low = np.array([-0.06, 0.0, -0.06])  # creux intra-journalier depuis l'ouverture du jour
    close_only = barrier_probability(daily, target=0.10, max_loss=0.10, daily_loss=0.05, n_boot=400, seed=6, max_days=50)
    intraday = barrier_probability(daily, target=0.10, max_loss=0.10, daily_loss=0.05, n_boot=400, seed=6, max_days=50,
                                   daily_low=low)
    assert close_only.p_daily_loss == 0.0                    # la clôture seule laisse passer
    assert close_only.equity_basis == "close_only"           # ... et le résultat le dit
    # tout chemin qui tire un jour à -6 % intra-jour échoue : 2 jours sur 3 sont de ce type
    assert intraday.equity_basis == "intraday"
    assert intraday.p_daily_loss > 0.95


def test_intraday_low_breaches_the_static_max_loss_even_if_the_close_recovers():
    daily = np.array([-0.02])
    low = np.array([-0.04])
    safe = barrier_probability(daily, target=0.50, max_loss=0.10, daily_loss=None, n_boot=50, seed=7, max_days=1,
                               daily_low=low)
    assert safe.p_max_loss == 0.0
    # deuxième jour: l'équité d'ouverture est 0,98 ; un creux de -9 % la mène à 0,89 < 0,90
    daily2 = np.array([-0.02, -0.02])
    low2 = np.array([-0.02, -0.09])
    rule = barrier_probability(daily2, target=0.50, max_loss=0.10, daily_loss=None, n_boot=50, seed=7, max_days=2,
                               daily_low=low2, block=2)
    # les blocs de 2 jours sont tirés à partir d'un début aléatoire : le chemin (jour 0, jour 1) arrive 1 fois sur 2
    assert 0.2 < rule.p_max_loss < 0.8


def test_daily_low_is_resampled_jointly_with_the_close():
    daily = np.array([0.01, -0.03])
    low = np.array([0.0, -0.06])
    res = barrier_probability(daily, target=0.20, max_loss=0.30, daily_loss=0.05, n_boot=2000, seed=8, max_days=200,
                              daily_low=low)
    # un chemin ne survit que s'il ne tire jamais le jour à -6 % : sur 200 jours, probabilité nulle
    assert res.p_daily_loss > 0.99


def test_daily_low_validation():
    with pytest.raises(ValueError):
        barrier_probability(np.array([-0.03]), target=0.1, max_loss=0.1, daily_loss=0.05, n_boot=10, seed=1,
                            daily_low=np.array([-0.01]))  # un creux ne peut pas être au-dessus de la clôture
    with pytest.raises(ValueError):
        barrier_probability(np.array([0.01, 0.0]), target=0.1, max_loss=0.1, daily_loss=0.05, n_boot=10, seed=1,
                            daily_low=np.array([-0.01]))  # mauvaise longueur
