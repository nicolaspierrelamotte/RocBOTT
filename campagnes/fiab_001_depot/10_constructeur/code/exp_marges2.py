import sys; sys.path.insert(0,"/home/user/RocBOTT/tests")
from test_lab_execution import *
for st,tg in [(10,30),(30,10)]:
    p = Pipeline(hashed_coin_signal, stop_bp=st, target_bp=tg, max_hold=5)
    r = zero_drift_control(p, n_paths=20, n_bars=5_000, sigma_bp=10.0, seed=31)
    print(st,tg,r.n_trades,"mean %.4f exp %.4f t_ex %.2f rawt %.2f"%(r.mean_r,r.expected_r,r.t_excess,r.t))
