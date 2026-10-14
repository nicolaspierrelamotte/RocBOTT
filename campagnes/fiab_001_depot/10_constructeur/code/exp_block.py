import numpy as np
from lab.ftmo import barrier_probability
# 200 jours : 190 jours +0.4 %, une grappe de 8 jours à -2 % consécutifs (-16 %)
r=np.full(200,0.004); r[50:58]=-0.02
for b in (1,8):
    res=barrier_probability(r,target=0.10,max_loss=0.10,daily_loss=None,n_boot=1500,seed=1,max_days=400,block=b)
    print(b,res)
