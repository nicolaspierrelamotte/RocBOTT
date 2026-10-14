import sys; sys.path.insert(0,"/home/user/RocBOTT/tests")
from test_power import *
res = power_curve(pipeline(), edges_bp=[0, 4, 8], n_trades=150, n_reps=40, sigma_bp=SIGMA, seed=20, t_threshold=THRESHOLD)
for r in res: print(r.edge_bp, r.detection_probability, (round(r.ci_low,3),round(r.ci_high,3)), round(r.realised_edge_bp,2), round(r.mean_t_excess,2))
r=power_curve(pipeline(), edges_bp=[5], n_trades=150, n_reps=60, sigma_bp=SIGMA, seed=21, t_threshold=THRESHOLD)[0]
print(r.detection_probability, (round(r.ci_low,3),round(r.ci_high,3)), NormalDist().cdf(r.mean_t_excess-THRESHOLD), r.mean_t_excess)
for n in (60,450):
    r=power_curve(pipeline(), edges_bp=[4], n_trades=n, n_reps=30, sigma_bp=SIGMA, seed=22, t_threshold=THRESHOLD)[0]
    print(n, r.detection_probability, r.mean_t_excess)
