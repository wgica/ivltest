from predict_round import *
def sim_round(p1,p2):
  scores=[(0,10),(1,8),(2,7),(2,6),(3,6),(3,5),
  (4,4),(5,5),(5,3),(6,3),(6,2),(7,2),(8,1),(10,0)]
  res=[]
  res.append(p1[0]*p2[0])
  res.append(p1[0]*p2[1]+p1[1]*p2[0])
  res.append(p1[0]*p2[2]+p1[2]*p2[0])
  res.append(p1[1]*p2[1])
  res.append(p1[0]*p2[3]+p1[3]*p2[0])
  res.append(p1[1]*p2[2]+p1[2]*p2[1])
  res.append(p1[1]*p2[3]+p1[2]*p2[2]+p1[3]*p2[1])
  res.append(p1[0]*p2[4]+p1[4]*p2[0])
  res.append(p1[2]*p2[3]+p1[3]*p2[2])
  res.append(p1[1]*p2[4]+p1[4]*p2[1])
  res.append(p1[3]*p2[3])
  res.append(p1[2]*p2[4]+p1[4]*p2[2])
  res.append(p1[3]*p2[4]+p1[4]*p2[3])
  res.append(p1[4]*p2[4])
  return res
def sim_bo3(statA, statB):
  # 初始化 2x5x7 的最终全零结果表
  res = [[[0 for _ in range(7)] for _ in range(5)] for i in range(2)]
  diffs = [-10,-7,-5,-4,-3,-2,0,0,2,3,4,5,7,10]

  # 内部工具函数：获取某一局的 14 种比分概率列表
  def get_round_pg(r):
    sA, hA = statA[r-1], statA[r+2]
    sB, hB = statB[r-1], statB[r+2]
    return sim_round(get_prob(sA, hB), get_prob(hA, sB))

  # --- 第一局 ---
  pg1 = get_round_pg(1)
  
  # --- 第二局 ---
  pg2 = get_round_pg(2)
  
  # 状态转移：打完前两局的所有可能状态
  # 每一项格式: (总分差, 净胜局, 平局数, 累计概率)
  st2 = []
  for i, p1 in enumerate(pg1):
    if p1 == 0: continue
    for j, p2 in enumerate(pg2):
      if p2 == 0: continue
      
      # 第一局状态
      d1 = diffs[i]
      nw1 = 1 if d1 > 0 else (-1 if d1 < 0 else 0)
      dc1 = 1 if d1 == 0 else 0
      
      # 第二局叠加
      d2 = diffs[j]
      nw2 = nw1 + (1 if d2 > 0 else (-1 if d2 < 0 else 0))
      dc2 = dc1 + (1 if d2 == 0 else 0)
      
      p_curr = p1 * p2
      
      # 核心：在这里直接拦截 2:0 提前结束的分支！不让它们进入第三局
      if nw2 == 2:
        res[1][4][3] += p_curr
      elif nw2 == -2:
        res[0][0][3] += p_curr
      else:
        # 没触发提前结束的，保留进入第三局
        st2.append((d1 + d2, nw2, dc2, p_curr))

  # --- 第三局 (只有没提前结束的才会走到这里) ---
  pg3 = get_round_pg(3)
  
  for sd, nw, dc, p_st2 in st2:
    for k, p3 in enumerate(pg3):
      if p3 == 0: continue
      
      # 第三局叠加
      d3 = diffs[k]
      final_sd = sd + d3
      final_nw = nw + (1 if d3 > 0 else (-1 if d3 < 0 else 0))
      final_dc = dc + (1 if d3 == 0 else 0)
      final_p = p_st2 * p3
      
      # 最终结算写入 res 数组
      if final_nw > 0:
        res[1][final_nw+2][-final_dc+3] += final_p
      elif final_nw < 0:
        res[0][final_nw+2][final_dc+3] += final_p
      else: # 大分平，比小分
        if final_sd > 0: res[1][2][-final_dc+3] += final_p
        elif final_sd < 0: res[0][2][final_dc+3] += final_p
        else:
          res[1][2][-final_dc+3] += final_p / 2
          res[0][2][final_dc+3] += final_p / 2

  # 打印非零输出
#    for i in range(2):
#        for j in range(5):
#            for k in range(7):
#                if res[i][j][k] > 0:
#                    print(i, j-2, k-3, "{:.2f}%".format(res[i][j][k]*100))
  return res
