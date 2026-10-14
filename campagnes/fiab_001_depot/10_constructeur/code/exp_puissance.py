"""Exploratoire (lot A) : courbe de puissance par avantage par trade."""
import sys, time, numpy as np
from lab.control import Pipeline, power_curve, minimum_detectable_edge
def follow(b): return np.sign(b.close-b.open).astype(int)
if __name__=="__main__":
    ntr=int(sys.argv[1]); reps=int(sys.argv[2])
    p=Pipeline(follow, stop_bp=15,target_bp=15,max_hold=5,half_spread_bp=0.0)
    t0=time.time()
    res=power_curve(p,edges_bp=[0,1,2,4,8],n_trades=ntr,n_reps=reps,sigma_bp=10,seed=20,t_threshold=3.6,n_bars=1500)
    for r in res: print(r)
    print("MDE80", minimum_detectable_edge(res), "%.0fs"%(time.time()-t0))
