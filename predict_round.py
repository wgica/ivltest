from math import exp
import math
from ti_math import eval_ti

def get_prob(mA,mB):
  scores=[(0,5),(1,3),(2,2),(3,1),(5,0)]
  
  def p_pois(m,k):
    if m==0:
      return 1.0 if k==0 else 0.0
    return m**k*exp(-m)/int(eval_ti(str(k)+"!"))

  raw=[]
  s_raw=0.0
  for pA,pB in scores:
    p=p_pois(mA,pA)*p_pois(mB,pB)
    raw.append(p)
    s_raw+=p

#  print("-[A:{} vs B:{}]-".format(mA,mB))
  res=[]
  for i , (pA,pB) in enumerate(scores):
    res.append(raw[i]/s_raw if s_raw>0 else 1/len(scores))
#    print("{}:{} -> {:.1f}%".format(pA,pB,res*100))
  return res
#print(get_prob(2.00,2.11))