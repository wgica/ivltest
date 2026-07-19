from random import *
from predict_bo3 import sim_bo3
import math
from collections import OrderedDict

teams=("act","dou5","fpx.zq","gg","gr","mrc","te","wbg","wolves","gw")

now_score={
"gr"         :[7,2,9,-3],
"gg"        :[6,3,5,-6],
"wbg"     :[6,3,2,-2],
"fpx.zq"  :[6,3,2,-1],
"act"       :[5,4,-2,1],
"te"         :[4,5,0,2],
"wolves":[3,6,-2,2],
"mrc"     :[3,6,-3,-1],
"gw"       :[3,6,-6,5],
"dou5"    :[2,7,-6,3]
}
stats={"gr":[1.56,1.89,1.50,3.22,3.56,2.50],
     "wbg":[1.00,2.00,1.86,3.22,3.33,3.00],
     "fpx.zq":[1.11,0.89,1.78,4.11,2.33,3.33],
     "gg":[1.44,1.78,1.57,3.11,2.89,2.71],
     "te":[1.22,1.56,1.13,3.00,3.00,2.50],
     "gw":[0.67,1.33,1.29,3.22,2.89,2.86],
     "mrc":[1.33,1.11,0.83,2.78,2.89,2.33],
     "wolves":[1.44,1.67,1.75,2.33,2.11,2.50],
     "act":[1.11,1.00,1.25,3.44,2.00,2.88],
     "dou5":[1.56,1.67,1.29,2.00,2.56,2.29]
}

def ran_sel(res):
  r=random()
  for i in range(2):
    for j in range(5):
      for k in range(7):
        r-=res[i][j][k]
        if r<0: 
          return i,j,k

resall=[[-1]*10 for _ in range(10)]

for i,t1 in enumerate(teams):
  for j in range(i+1,10):
    t2=teams[j]
    resall[i][j]=sim_bo3(stats[t1],stats[t2])
def one_test():
  new_score={k:v[:] for k,v in now_score.items()}
  #print(new_score)
  for i,t1 in enumerate(teams):
    for j in range(i+1,10):
      t2=teams[j]
      if t2==t1: continue
      #res=sim_bo3(stats[t1],stats[t2])
      res=resall[i][j]
      i,j,k=ran_sel(res)
      j-=2
      k-=3
      a,b,c,d=new_score[t1]
      e,f,g,h=new_score[t2]
      if i==1:
        a+=1
        f+=1
      else:
        b+=1
        e+=1
      c+=j
      g-=j
      d+=k
      h-=k
      new_score[t1]=a,b,c,d
      new_score[t2]=e,f,g,h

  sorted_score=OrderedDict(
  sorted(
  new_score.items(),
  key=lambda x: (-x[1][0],-x[1][2],-x[1][3])
  ))
#  for k,v in sorted_score.items():
#    print(k,v)
#    print(k,": W",v[0],"L",v[1],"N",v[2],"D",v[3])
  return sorted_score.keys()
print("----Stage 1----")
all_res=[[0]*10 for _ in range(10)]
for _ in range(1000):
  test_res=one_test()
  for i,t in enumerate(teams):
    pos=list(test_res).index(t)
    all_res[i][pos]+=1
print("----Stage 2----")
for i,t in enumerate(teams):
  print(t,end=" ")
  print("{:.1f}%".format(sum(all_res[i][0:4])/10),end=" ")
  print("{:.1f}%".format(sum(all_res[i][4:6])/10),end=" ")
  print("{:.1f}%".format(sum(all_res[i][6:8])/10),end=" ")
  print("{:.1f}%".format(sum(all_res[i][8:10])/10),end=" ")
  ax=0
  for j,p in enumerate(all_res[i]): 
    ax+=p*(j+1)
  print("{:.2f}".format(ax/1000))
  for j in all_res[i]:
    print("{:.1f}%".format(j/10),sep="",end=" ")
  print("")