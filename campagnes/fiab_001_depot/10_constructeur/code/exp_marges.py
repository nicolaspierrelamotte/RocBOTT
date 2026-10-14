import sys; sys.path.insert(0,"/home/user/RocBOTT/tests")
import numpy as np
from test_colibri_reproduction import *
for name,f in [("leaky",outside_bar_filter),("causal",causal_outside_bar_filter),("none",None)]:
    r=zero_drift_control(make_pipeline(f), n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=10)
    print(name, r.n_trades, "excess %.4f t_ex %.2f raw t %.2f"%(r.excess_r,r.t_excess,r.t))
kw = dict(n_paths=20, n_bars=5_000, sigma_bp=SIGMA, seed=13)
for nm,sig in [("clean",follow_last_bar),("leaky10",partial_future_signal(0.10))]:
    r=zero_drift_control(Pipeline(sig, stop_bp=20, target_bp=20, max_hold=5, half_spread_bp=0.5), **kw)
    print(nm, r.n_trades, r.expected_r, "t_ex %.2f raw t %.2f"%(r.t_excess,r.t))
bars = random_walk_bars(5_000, sigma_bp=SIGMA, seed=11)
for f in (outside_bar_filter, causal_outside_bar_filter):
    print(detect_leak(make_pipeline(f), bars, sigma_bp=SIGMA, seed=12, n_checks=150))
