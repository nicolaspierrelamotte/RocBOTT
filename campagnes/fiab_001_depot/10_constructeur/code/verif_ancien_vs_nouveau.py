"""Lot A : les mêmes constats, rejoués contre l'ancien code (c9d69b9) puis contre le nouveau.

Usage : PYTHONPATH=<dossier contenant lab/> python3 verif_ancien_vs_nouveau.py
Chaque ligne : identifiant, résultat observé. Un constat « DÉFAUT » sur l'ancien code
et « ok » sur le nouveau est ce qui justifie le test correspondant du dépôt.
"""
import inspect
import numpy as np

import lab
from lab.control import Pipeline, zero_drift_control
from lab.simulate import Trade, outside_bar_filter, r_stats, simulate_trades
from lab.synthetic import BP, Bars, random_walk_bars
from lab.acausality import detect_leak
from lab.ftmo import barrier_probability

print("lab importé depuis", lab.__file__)


def follow(b):
    return np.sign(b.close - b.open).astype(int)


_RealPipeline = Pipeline


def Pipeline(*a, **kw):  # noqa: N802  (enveloppe : même appel contre l'ancien et le nouveau code)
    if "allow_known_acausal" in inspect.signature(_RealPipeline).parameters:
        kw.setdefault("allow_known_acausal", True)
    return _RealPipeline(*a, **kw)


def check(name, fn):
    try:
        verdict = fn()
    except Exception as e:  # noqa: BLE001
        verdict = f"ERREUR {type(e).__name__}: {str(e)[:90]}"
    print(f"{name:55s} {verdict}")


def bars_from(ohlc):
    o, h, l, c = (np.array(x, dtype=float) for x in zip(*ohlc))
    return Bars(o, h, l, c)


def f4_gap():
    b = bars_from([(100, 100, 100, 100), (100, 100.01, 99.99, 100), (99.5, 99.6, 99.4, 99.5)])
    sig = np.zeros(3, dtype=int)
    sig[0] = 1
    r = simulate_trades(b, sig, stop_bp=10, target_bp=30, max_hold=5)[0].r
    return f"R stop sur gap = {r:+.2f} ({'ok' if abs(r + 5) < 1e-9 else 'DÉFAUT : attendu -5'})"


def f4_asym():
    p = Pipeline(follow, stop_bp=10, target_bp=30, max_hold=5)
    r = zero_drift_control(p, n_paths=20, n_bars=5000, sigma_bp=10, seed=31)
    if hasattr(r, "t_excess"):
        return f"t_excess = {r.t_excess:+.2f} ({'ok' if abs(r.t_excess) < 3 else 'DÉFAUT'})"
    return f"R brut {r.mean_r:+.4f} vs attendu {r.expected_r_from_spread:+.4f}, t = {r.t:+.2f} : DÉFAUT (zéro faux)"


def f5_clean_with_spread():
    p = Pipeline(follow, stop_bp=20, target_bp=20, max_hold=5, spread_bp=1.0) if "half_spread_bp" not in inspect.signature(_RealPipeline).parameters else Pipeline(follow, stop_bp=20, target_bp=20, max_hold=5, half_spread_bp=0.5)
    r = zero_drift_control(p, n_paths=20, n_bars=5000, sigma_bp=10, seed=13)
    crit = getattr(r, "t_excess", r.t)
    return f"critère = {crit:+.2f} ({'refusé à tort' if abs(crit) >= 3 else 'ok : pipeline propre accepté'})"


def f5_leak_with_spread():
    def sig(bars):
        base = follow(bars)
        fut = np.zeros_like(base)
        fut[:-1] = base[1:]
        mask = (np.arange(len(bars)) * 2654435761 % 1000) < 100
        return np.where(mask, fut, base)

    sig.__qualname__ = "partial_future"
    kw = dict(half_spread_bp=0.5) if "half_spread_bp" in inspect.signature(_RealPipeline).parameters else dict(spread_bp=1.0)
    p = Pipeline(sig, stop_bp=20, target_bp=20, max_hold=5, **kw)
    r = zero_drift_control(p, n_paths=20, n_bars=5000, sigma_bp=10, seed=13)
    crit = getattr(r, "t_excess", r.t)
    return f"critère = {crit:+.2f} ({'fuite laissée passer' if abs(crit) < 3 else 'ok : fuite signalée'})"


def f2_pipeline_detect():
    p = Pipeline(follow, stop_bp=15, target_bp=15, max_hold=5, population_filter=outside_bar_filter)
    bars = random_walk_bars(3000, sigma_bp=10, seed=11)
    rep = detect_leak(p, bars, sigma_bp=10, seed=12, n_checks=100)
    return f"n_changed = {rep.n_changed} / {rep.n_checked} ({'ok : fuite signalée' if rep.leaks else 'DÉFAUT'})"


def f2_decide_without_filter():
    """Une decide = pipeline.signal (sans filtre) certifie la chaîne : défaut de l'ancien code."""
    p = Pipeline(follow, stop_bp=15, target_bp=15, max_hold=5, population_filter=outside_bar_filter)
    bars = random_walk_bars(3000, sigma_bp=10, seed=11)
    rep = detect_leak(p.signal, bars, sigma_bp=10, seed=12, n_checks=100)
    return f"decide = signal seul : n_changed = {rep.n_changed} (attendu 0 des deux côtés : un signal nu ne porte pas le filtre ; d'où Pipeline.decide)"


def f7_half_spread():
    b = bars_from([(100, 100, 100, 100), (100, 100.085, 100, 100.0), (100, 100, 100, 100)])
    sig = np.zeros(3, dtype=int)
    sig[0] = -1
    return str(simulate_trades(b, sig, stop_bp=10, target_bp=30, max_hold=5, half_spread_bp=1.0)[0].exit_bar)


def f12_intraday():
    return str(barrier_probability(np.array([-0.03, 0.02, -0.03]), target=0.1, max_loss=0.1, daily_loss=0.05,
                                   n_boot=200, seed=6, max_days=50, daily_low=np.array([-0.06, 0.0, -0.06])).p_daily_loss)


def f12_close_only():
    r = barrier_probability(np.array([-0.03, 0.02, -0.03]), target=0.1, max_loss=0.1, daily_loss=0.05,
                            n_boot=200, seed=6, max_days=50)
    return f"p_daily_loss = {r.p_daily_loss} sur clôtures seules (aucun champ ne dit que le creux est ignoré)" + (
        f" ; equity_basis = {r.equity_basis}" if hasattr(r, "equity_basis") else "")


def f26():
    return str(r_stats([Trade(0, 1, 2, 1, -0.5) for _ in range(5)])["t"])


def f8_power():
    from lab.control import power_curve  # noqa: F401
    return "power_curve présent"


check("F-4 stop sur gap", f4_gap)
check("F-4 zéro du témoin, stop 10 / objectif 30", f4_asym)
check("F-5 pipeline propre, péage non nul", f5_clean_with_spread)
check("F-5 fuite de l'ordre du péage", f5_leak_with_spread)
check("F-2 detect_leak(Pipeline)", f2_pipeline_detect)
check("F-2 decide = signal seul", f2_decide_without_filter)
check("F-7 demi-écart bid/ask", f7_half_spread)
check("F-12 creux intra-journalier fourni", f12_intraday)
check("F-12 clôtures seules", f12_close_only)
check("F-26 t pour sd=0, R<0", f26)
check("F-8 courbe de puissance par probabilité", f8_power)
