"""Reproduit le mode de défaillance de Colibri sur une marche à dérive nulle.

Signal : sens de la barre qui vient de clore (suivi naïf). Filtre : jeter les
trades dont la barre d'ENTRÉE est externe. Ce filtre regarde le futur ;
il doit fabriquer un R positif sur du bruit pur et être attrapé par le
détecteur, appelé sur le ``Pipeline`` lui-même (aucune ``decide`` recopiée à la
main, F-2). La même règle appliquée à la barre de décision est causale.

Le critère du témoin est ``t_excess`` : t de (R - R attendu), R attendu CALCULÉ
(F-4, F-5). Le t du R brut n'est pas un critère : le péage le décale.
"""
import numpy as np
import pytest

from lab.acausality import detect_leak, detect_trade_leak
from lab.control import InconclusiveError, Pipeline, zero_drift_control
from lab.simulate import causal_outside_bar_filter, outside_bar_filter
from lab.synthetic import random_walk_bars

SIGMA = 10.0


def follow_last_bar(bars):
    return np.sign(bars.close - bars.open).astype(int)


def future_bar_direction(bars):
    """Signal qui lit le FUTUR : sens de la barre suivante (fuite portée par le signal, pas le filtre)."""
    nxt = np.sign(bars.close - bars.open).astype(int)
    out = np.zeros_like(nxt)
    out[:-1] = nxt[1:]
    return out


def make_pipeline(pop_filter, signal=follow_last_bar, **kw):
    return Pipeline(signal, stop_bp=15, target_bp=15, max_hold=5, population_filter=pop_filter,
                    allow_known_acausal=True, **kw)


def test_acausal_filter_fabricates_excess_on_pure_noise():
    leaky = zero_drift_control(make_pipeline(outside_bar_filter), n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=10)
    clean = zero_drift_control(make_pipeline(causal_outside_bar_filter), n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=10)
    none = zero_drift_control(make_pipeline(None), n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=10)
    assert leaky.t_excess > 3, leaky      # le témoin à dérive nulle sonne sur l'écart au R attendu
    assert leaky.excess_r > 0.01, leaky
    assert abs(clean.t_excess) < 3, clean  # la version causale reste à zéro
    assert abs(none.t_excess) < 3, none


def test_detector_called_on_the_pipeline_flags_acausal_filter_and_clears_causal_one():
    """F-2 : le détecteur reçoit le Pipeline ; ni signal ni filtre recopiés à la main."""
    bars = random_walk_bars(5_000, sigma_bp=SIGMA, seed=11)
    leaky = detect_leak(make_pipeline(outside_bar_filter), bars, sigma_bp=SIGMA, seed=12, n_checks=150)
    causal = detect_leak(make_pipeline(causal_outside_bar_filter), bars, sigma_bp=SIGMA, seed=12, n_checks=150)
    assert leaky.conclusive and leaky.leaks and leaky.leak_rate > 0.05, leaky
    assert causal.conclusive and not causal.leaks, causal


def test_signal_that_reads_the_future_is_caught_through_the_pipeline_even_without_filter():
    bars = random_walk_bars(3_000, sigma_bp=SIGMA, seed=14)
    p = make_pipeline(None, signal=future_bar_direction)
    rep = detect_leak(p, bars, sigma_bp=SIGMA, seed=15, n_checks=100)
    assert rep.leaks and rep.leak_rate > 0.3, rep


def test_trade_level_detector_runs_the_executed_chain_and_agrees():
    bars = random_walk_bars(2_000, sigma_bp=SIGMA, seed=16)
    leaky = detect_trade_leak(make_pipeline(outside_bar_filter), bars, sigma_bp=SIGMA, seed=17, n_checks=40)
    signal_leak = detect_trade_leak(make_pipeline(None, signal=future_bar_direction), bars, sigma_bp=SIGMA, seed=17,
                                    n_checks=40)
    causal = detect_trade_leak(make_pipeline(causal_outside_bar_filter), bars, sigma_bp=SIGMA, seed=17, n_checks=40)
    assert leaky.leaks and signal_leak.leaks
    assert causal.conclusive and not causal.leaks, causal


def test_pipeline_decide_is_what_simulate_trades_executes():
    """Chaque trade exécuté correspond à une décision non nulle de ``decide``, de même sens ; pas de décision orpheline en position libre."""
    bars = random_walk_bars(3_000, sigma_bp=SIGMA, seed=18)
    for flt in (outside_bar_filter, causal_outside_bar_filter, None):
        p = make_pipeline(flt)
        dec = p.decide(bars)
        trades = p.run_trades(bars)
        assert trades
        assert all(dec[tr.decision_bar] == tr.direction for tr in trades)
        # et le filtre est bien dans decide : une decide = signal seul compterait plus de décisions
        if flt is not None:
            assert (dec != 0).sum() < (follow_last_bar(bars)[:-1] != 0).sum()


def partial_future_signal(fraction):
    """Signal suiveur qui lit le futur sur une fraction fixe des barres (fuite dosée, déterministe)."""

    def sig(bars):
        base = follow_last_bar(bars)
        fut = future_bar_direction(bars)
        mask = (np.arange(len(bars)) * 2654435761 % 1000) < fraction * 1000
        return np.where(mask, fut, base)

    sig.__qualname__ = f"partial_future_signal_{fraction}"
    return sig


def test_spread_does_not_mask_a_leak_and_does_not_condemn_a_clean_pipeline():
    """F-5 : avec péage, le t du R brut est décalé ; t_excess ne l'est pas.

    Pipeline propre à péage non nul : t brut très négatif (l'ancien critère
    |t| < 3 l'aurait refusé), t_excess dans ±3. Même pipeline avec une fuite de
    l'ordre du péage (10 % des décisions lisent le futur) : t brut proche de 0
    (l'ancien critère l'aurait laissé passer), t_excess franchement positif.
    """
    kw = dict(n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=13)

    def pipe(sig):
        return Pipeline(sig, stop_bp=20, target_bp=20, max_hold=5, half_spread_bp=0.5)

    clean = zero_drift_control(pipe(follow_last_bar), **kw)
    leaky = zero_drift_control(pipe(partial_future_signal(0.10)), **kw)
    assert clean.t < -5, clean              # le péage tire le t brut vers le négatif
    assert abs(clean.t_excess) < 3, clean   # ... mais pas l'écart au R attendu
    assert abs(leaky.t) < 3, leaky          # la fuite est masquée dans le t brut
    assert leaky.t_excess > 4, leaky        # ... et révélée par l'écart au R attendu
    assert clean.expected_r == pytest.approx(-0.05, abs=0.01)  # 2 × 0,5 bp / 20 bp, à la mécanique près


def test_inconclusive_control_has_no_t_and_is_not_conclusive():
    """F-3 : un pipeline qui ne trade jamais n'a pas de témoin (NaN, conclusive=False), pas un zéro."""
    never = Pipeline(lambda b: np.zeros(len(b), dtype=int), stop_bp=15, target_bp=15, max_hold=5)
    res = zero_drift_control(never, n_paths=3, n_bars=500, sigma_bp=SIGMA, seed=1)
    assert res.n_trades == 0 and not res.conclusive and np.isnan(res.t_excess)


def test_known_acausal_filter_is_refused_unless_explicit():
    """F-27 : garde contre l'import involontaire du filtre de Colibri dans une chaîne."""
    with pytest.raises(ValueError):
        Pipeline(follow_last_bar, stop_bp=15, target_bp=15, max_hold=5, population_filter=outside_bar_filter)


def test_pipeline_fingerprint_changes_with_signal_filter_and_parameters():
    a = make_pipeline(None).fingerprint()
    assert a != make_pipeline(causal_outside_bar_filter).fingerprint()
    assert a != make_pipeline(None, signal=future_bar_direction).fingerprint()
    assert a != Pipeline(follow_last_bar, stop_bp=16, target_bp=15, max_hold=5).fingerprint()
