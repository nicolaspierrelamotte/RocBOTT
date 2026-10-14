"""Exploratoire (lot A) : un pipeline qui lit le futur sur une fraction f des décisions, avec péage."""
import numpy as np
from lab.control import Pipeline, zero_drift_control
def follow(b): return np.sign(b.close-b.open).astype(int)
def make_partial(f):
    def sig(b):
        s=follow(b)
        fut=np.sign(np.roll(b.close,-1)-np.roll(b.open,-1)).astype(int)
        fut[-1]=0
        mask=(np.arange(len(b))*2654435761 % 1000) < f*1000
        return np.where(mask,fut,s)
    sig.__qualname__=f"partial_future_{f}"
    return sig
if __name__=="__main__":
    for f in [0.0,0.05,0.1,0.2]:
        p=Pipeline(make_partial(f), stop_bp=20,target_bp=20,max_hold=5,half_spread_bp=0.5)
        r=zero_drift_control(p,n_paths=20,n_bars=5000,sigma_bp=10,seed=13)
        print(f, r.n_trades, "mean %.4f exp %.4f excess %.4f t_ex %.2f rawt %.2f"%(r.mean_r,r.expected_r,r.excess_r,r.t_excess,r.t))
