from random import *
import math
import argparse
import time

FACTORIALS = [1, 1, 2, 6, 24, 120]

teams = ("act", "dou5", "fpx.zq", "gg", "gr", "mrc", "te", "wbg", "wolves", "gw")

parser = argparse.ArgumentParser(description='IVL联赛排名预测分析')
parser.add_argument('--no-input', action='store_true', help='跳过交互式输入，使用默认值')
parser.add_argument('--data', default='stats.txt', help='stats数据文件路径')
parser.add_argument('--sim', type=int, default=100000, choices=[100000, 1000000],
                    help='模拟次数: 100000(10万) 或 1000000(100万)，默认10万')
args = parser.parse_args()


def load_stats_from_file(filepath="stats.txt"):
    stats = {}
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 8:
                continue
            team_name = parts[0].lower()
            nums = [float(p) for p in parts[1:]]
            stats[team_name] = [nums[0], nums[1], nums[2], nums[4], nums[5], nums[6]]
    return stats


DEFAULT_NOW_SCORE = {
    "gr": [7, 2, 9, -3],
    "gg": [6, 3, 5, -6],
    "wbg": [6, 3, 2, -2],
    "fpx.zq": [6, 3, 2, -1],
    "act": [5, 4, -2, 1],
    "te": [4, 5, 0, 2],
    "wolves": [3, 6, -2, 2],
    "mrc": [3, 6, -3, -1],
    "gw": [3, 6, -6, 5],
    "dou5": [2, 7, -6, 3]
}


def load_saved_scores(filepath="now_score.json"):
    try:
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict) and all(t in data for t in teams):
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return DEFAULT_NOW_SCORE


def save_scores(now_score, filepath="now_score.json"):
    import json
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(now_score, f, indent=2, ensure_ascii=False)


def input_now_score():
    saved_scores = load_saved_scores()
    if args.no_input:
        print("使用已保存的积分数据\n")
        save_scores(saved_scores)
        return saved_scores
    
    now_score = {}
    print("请输入各队伍当前积分 (格式: 胜场 负场 净胜局 净胜分)")
    print("直接按回车使用上次保存的值\n")
    for team in teams:
        saved = saved_scores.get(team, DEFAULT_NOW_SCORE.get(team, [0, 0, 0, 0]))
        prompt = f"{team.upper()} [{saved[0]} {saved[1]} {saved[2]} {saved[3]}]: "
        try:
            user_input = input(prompt).strip()
            if user_input:
                values = list(map(int, user_input.split()))
                if len(values) == 4:
                    now_score[team] = values
                else:
                    print(f"  格式错误，使用上次保存的值")
                    now_score[team] = saved
            else:
                now_score[team] = saved
        except ValueError:
            print(f"  输入错误，使用上次保存的值")
            now_score[team] = saved
    
    save_scores(now_score)
    print("\n积分数据已自动保存\n")
    return now_score


stats = load_stats_from_file(args.data)
now_score = input_now_score()


def get_all_possible_matches():
    matches = []
    for i, t1 in enumerate(teams):
        for j in range(i + 1, len(teams)):
            t2 = teams[j]
            matches.append((t1, t2))
    return matches


DEFAULT_REMAINING_MATCHES = get_all_possible_matches()


def load_remaining_matches(filepath="remaining_matches.txt"):
    matches = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    t1 = parts[0].lower()
                    t2 = parts[1].lower()
                    if t1 in teams and t2 in teams and t1 != t2:
                        matches.append((t1, t2))
        if matches:
            return matches
    except FileNotFoundError:
        pass
    return DEFAULT_REMAINING_MATCHES


remaining_matches = load_remaining_matches()
print(f"已加载 {len(remaining_matches)} 场剩余比赛")


def get_prob(mA, mB):
    scores = [(0, 5), (1, 3), (2, 2), (3, 1), (5, 0)]

    def p_pois(m, k):
        if m == 0:
            return 1.0 if k == 0 else 0.0
        return m ** k * math.exp(-m) / FACTORIALS[k]

    raw = [0.0] * 5
    s_raw = 0.0
    for i, (pA, pB) in enumerate(scores):
        p = p_pois(mA, pA) * p_pois(mB, pB)
        raw[i] = p
        s_raw += p

    if s_raw > 0:
        for i in range(5):
            raw[i] /= s_raw
    else:
        for i in range(5):
            raw[i] = 0.2
    return raw


def sim_round(p1, p2):
    scores = [(0, 10), (1, 8), (2, 7), (2, 6), (3, 6), (3, 5),
              (4, 4), (5, 5), (5, 3), (6, 3), (6, 2), (7, 2), (8, 1), (10, 0)]
    res = []
    res.append(p1[0] * p2[0])
    res.append(p1[0] * p2[1] + p1[1] * p2[0])
    res.append(p1[0] * p2[2] + p1[2] * p2[0])
    res.append(p1[1] * p2[1])
    res.append(p1[0] * p2[3] + p1[3] * p2[0])
    res.append(p1[1] * p2[2] + p1[2] * p2[1])
    res.append(p1[1] * p2[3] + p1[2] * p2[2] + p1[3] * p2[1])
    res.append(p1[0] * p2[4] + p1[4] * p2[0])
    res.append(p1[2] * p2[3] + p1[3] * p2[2])
    res.append(p1[1] * p2[4] + p1[4] * p2[1])
    res.append(p1[3] * p2[3])
    res.append(p1[2] * p2[4] + p1[4] * p2[2])
    res.append(p1[3] * p2[4] + p1[4] * p2[3])
    res.append(p1[4] * p2[4])
    return res


def sim_bo3(statA, statB):
    res = [[[0 for _ in range(7)] for _ in range(5)] for i in range(2)]
    diffs = [-10, -7, -5, -4, -3, -2, 0, 0, 2, 3, 4, 5, 7, 10]

    def get_round_pg(r):
        sA, hA = statA[r - 1], statA[r + 2]
        sB, hB = statB[r - 1], statB[r + 2]
        return sim_round(get_prob(sA, hB), get_prob(hA, sB))

    pg1 = get_round_pg(1)
    pg2 = get_round_pg(2)

    st2 = []
    for i, p1 in enumerate(pg1):
        if p1 == 0:
            continue
        for j, p2 in enumerate(pg2):
            if p2 == 0:
                continue

            d1 = diffs[i]
            nw1 = 1 if d1 > 0 else (-1 if d1 < 0 else 0)
            dc1 = 1 if d1 == 0 else 0

            d2 = diffs[j]
            nw2 = nw1 + (1 if d2 > 0 else (-1 if d2 < 0 else 0))
            dc2 = dc1 + (1 if d2 == 0 else 0)

            p_curr = p1 * p2

            if nw2 == 2:
                res[1][4][3] += p_curr
            elif nw2 == -2:
                res[0][0][3] += p_curr
            else:
                st2.append((d1 + d2, nw2, dc2, p_curr))

    pg3 = get_round_pg(3)

    for sd, nw, dc, p_st2 in st2:
        for k, p3 in enumerate(pg3):
            if p3 == 0:
                continue

            d3 = diffs[k]
            final_sd = sd + d3
            final_nw = nw + (1 if d3 > 0 else (-1 if d3 < 0 else 0))
            final_dc = dc + (1 if d3 == 0 else 0)
            final_p = p_st2 * p3

            if final_nw > 0:
                res[1][final_nw + 2][-final_dc + 3] += final_p
            elif final_nw < 0:
                res[0][final_nw + 2][final_dc + 3] += final_p
            else:
                if final_sd > 0:
                    res[1][2][-final_dc + 3] += final_p
                elif final_sd < 0:
                    res[0][2][final_dc + 3] += final_p
                else:
                    res[1][2][-final_dc + 3] += final_p / 2
                    res[0][2][final_dc + 3] += final_p / 2

    return res


def ran_sel(res_flat):
    r = random()
    for idx, p in enumerate(res_flat):
        r -= p
        if r < 0:
            i = idx // 35
            j = (idx % 35) // 7
            k = idx % 7
            return i, j, k


team_index = {t: i for i, t in enumerate(teams)}

resall = [[-1] * 10 for _ in range(10)]

for t1, t2 in remaining_matches:
    i = team_index[t1]
    j = team_index[t2]
    if i < j:
        res = sim_bo3(stats[t1], stats[t2])
        flat = []
        for ii in range(2):
            for jj in range(5):
                for kk in range(7):
                    flat.append(res[ii][jj][kk])
        resall[i][j] = flat
    else:
        res = sim_bo3(stats[t2], stats[t1])
        flat = []
        for ii in range(2):
            for jj in range(5):
                for kk in range(7):
                    flat.append(res[ii][jj][kk])
        resall[j][i] = flat


def one_test():
    new_score = [list(now_score[t]) for t in teams]
    for t1, t2 in remaining_matches:
        i = team_index[t1]
        j = team_index[t2]
        if i < j:
            res = resall[i][j]
        else:
            res = resall[j][i]
        
        winner, nw, dc = ran_sel(res)
        nw -= 2
        dc -= 3
        
        if winner == 1:
            new_score[i][0] += 1
            new_score[j][1] += 1
        else:
            new_score[i][1] += 1
            new_score[j][0] += 1
        new_score[i][2] += nw
        new_score[j][2] -= nw
        new_score[i][3] += dc
        new_score[j][3] -= dc

    ranked = sorted(range(10), key=lambda x: (-new_score[x][0], -new_score[x][2], -new_score[x][3]))
    return ranked, new_score


SIMULATION_COUNT = args.sim
SIM_LABEL = "100k" if SIMULATION_COUNT == 100000 else "1M"

print("----Stage 1----")
print(f"模拟次数: {SIMULATION_COUNT:,} ({SIM_LABEL})")
start_time = time.time()
all_res = [[0] * 10 for _ in range(10)]
winner_line_sum = 0.0
playoff_a_line_sum = 0.0
playoff_b_line_sum = 0.0

for _ in range(SIMULATION_COUNT):
    ranked, new_score = one_test()
    
    for pos, idx in enumerate(ranked):
        all_res[idx][pos] += 1
    
    rank4_score = new_score[ranked[3]][0]
    rank5_score = new_score[ranked[4]][0]
    rank6_score = new_score[ranked[5]][0]
    rank7_score = new_score[ranked[6]][0]
    rank8_score = new_score[ranked[7]][0]
    rank9_score = new_score[ranked[8]][0]
    
    winner_line_sum += (rank4_score + rank5_score) / 2
    playoff_a_line_sum += (rank6_score + rank7_score) / 2
    playoff_b_line_sum += (rank8_score + rank9_score) / 2

winner_line = winner_line_sum / SIMULATION_COUNT
playoff_a_line = playoff_a_line_sum / SIMULATION_COUNT
playoff_b_line = playoff_b_line_sum / SIMULATION_COUNT

print(f"胜者组分数线: {winner_line:.2f}胜")
print(f"附加组A分数线: {playoff_a_line:.2f}胜")
print(f"附加组B分数线: {playoff_b_line:.2f}胜")
print("----Stage 2----")


def format_prob(count):
    prob = count / SIMULATION_COUNT * 100
    if prob < 0.01:
        return f"{count}次/{SIM_LABEL}"
    return f"{prob:.2f}%"


def generate_html_report(all_res, teams, winner_line, playoff_a_line, playoff_b_line):
    team_data = []
    for i, t in enumerate(teams):
        avg_rank = sum(p * (j + 1) for j, p in enumerate(all_res[i])) / SIMULATION_COUNT
        team_data.append((t, i, avg_rank))
    team_data.sort(key=lambda x: x[2])

    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IVL联赛排名预测分析</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Microsoft YaHei', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            color: white;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        h2 {
            color: #333;
            font-size: 1.5em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .subtitle {
            text-align: center;
            color: rgba(255,255,255,0.9);
            font-size: 1.1em;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            padding: 30px;
            margin-bottom: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9em;
            table-layout: fixed;
        }
        th, td {
            padding: 10px 6px;
            text-align: center;
            width: auto;
            border: 4px solid white;
        }
        th {
            color: white;
            font-weight: 700;
            font-size: 1.1em;
            position: sticky;
            top: 0;
            padding: 14px 6px;
            z-index: 10;
        }
        td {
            background: #f8f9fa;
            border-radius: 6px;
        }
        table.group-table th, table.group-table td {
            width: 16.67%;
        }
        table.group-table th:first-child {
            width: 12%;
            background: #333;
            border-radius: 6px;
        }
        table.group-table th:nth-child(2) {
            background: linear-gradient(135deg, #4CAF50, #66BB6A);
            border-radius: 6px;
        }
        table.group-table th:nth-child(3) {
            background: linear-gradient(135deg, #FF9800, #FFA726);
            border-radius: 6px;
        }
        table.group-table th:nth-child(4) {
            background: linear-gradient(135deg, #2196F3, #42A5F5);
            border-radius: 6px;
        }
        table.group-table th:nth-child(5) {
            background: linear-gradient(135deg, #F44336, #EF5350);
            border-radius: 6px;
        }
        table.group-table th:last-child {
            width: 12%;
            background: #333;
            border-radius: 6px;
        }
        table.rank-table th, table.rank-table td {
            width: 9.09%;
        }
        table.rank-table th:first-child {
            width: 12%;
            background: #333;
            color: white;
            border-radius: 6px;
        }
        table.rank-table th:not(:first-child) {
            background: #f8f9fa;
            color: #333;
            border-radius: 6px;
        }
        table.rank-table tbody tr:nth-child(1) td:first-child {
            background: linear-gradient(90deg, #FFD700, #FFA500);
            color: #333;
        }
        table.rank-table tbody tr:nth-child(2) td:first-child {
            background: linear-gradient(90deg, #C0C0C0, #A8A8A8);
            color: #333;
        }
        table.rank-table tbody tr:nth-child(3) td:first-child {
            background: linear-gradient(90deg, #CD7F32, #DAA520);
            color: #333;
        }
        table.rank-table tbody tr:nth-child(4) td:first-child {
            background: linear-gradient(90deg, #90EE90, #98FB98);
            color: #333;
        }
        table.rank-table tbody tr:nth-child(5) td:first-child,
        table.rank-table tbody tr:nth-child(6) td:first-child {
            background: linear-gradient(90deg, #87CEEB, #B0E0E6);
            color: #333;
        }
        table.rank-table tbody tr:nth-child(7) td:first-child,
        table.rank-table tbody tr:nth-child(8) td:first-child {
            background: linear-gradient(90deg, #DDA0DD, #EE82EE);
            color: #333;
        }
        table.rank-table tbody tr:nth-child(9) td:first-child,
        table.rank-table tbody tr:nth-child(10) td:first-child {
            background: linear-gradient(90deg, #F08080, #FA8072);
            color: #333;
        }
        tr:hover {
            background-color: #f5f7fa;
        }
        .bar-container {
            position: relative;
            height: 48px;
            background: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
            border: 1px solid #ddd;
        }
        .bar {
            height: 100%;
            border-radius: 2px;
            transition: width 0.3s ease;
        }
        .bar-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #333;
            font-weight: 800;
            font-size: 1.5em;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.9);
            white-space: nowrap;
        }
        .rank-bar {
            height: 16px;
            border-radius: 8px;
            margin: 2px 0;
        }
        .group-winner { background: linear-gradient(90deg, #4CAF50, #8BC34A); }
        .group-a { background: linear-gradient(90deg, #FF9800, #FFB74D); }
        .group-b { background: linear-gradient(90deg, #2196F3, #64B5F6); }
        .group-eliminate { background: linear-gradient(90deg, #F44336, #EF9A9A); }
        .rank-1 { background: linear-gradient(90deg, #FFD700, #FFA500); }
        .rank-2 { background: linear-gradient(90deg, #C0C0C0, #A8A8A8); }
        .rank-3 { background: linear-gradient(90deg, #CD7F32, #DAA520); }
        .rank-4 { background: linear-gradient(90deg, #90EE90, #98FB98); }
        .rank-5-6 { background: linear-gradient(90deg, #87CEEB, #B0E0E6); }
        .rank-7-8 { background: linear-gradient(90deg, #DDA0DD, #EE82EE); }
        .rank-9-10 { background: linear-gradient(90deg, #F08080, #FA8072); }
        .bar-gold { background: linear-gradient(90deg, #FFD700, #FFA500); }
        .bar-silver { background: linear-gradient(90deg, #C0C0C0, #A8A8A8); }
        .bar-bronze { background: linear-gradient(90deg, #CD7F32, #DAA520); }
        .bar-green { background: linear-gradient(90deg, #90EE90, #98FB98); }
        .bar-sky { background: linear-gradient(90deg, #87CEEB, #B0E0E6); }
        .bar-purple { background: linear-gradient(90deg, #DDA0DD, #EE82EE); }
        .bar-red { background: linear-gradient(90deg, #F08080, #FA8072); }
        .team-name {
            font-weight: 700;
            font-size: 1.1em;
            color: #333;
        }
        .avg-rank {
            font-weight: 700;
            font-size: 1.2em;
            color: #667eea;
        }
        .high-prob {
            color: #4CAF50;
            font-weight: 700;
        }
        .low-prob {
            color: #F44336;
            font-weight: 700;
        }
        .prob-value {
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            font-weight: 600;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .summary-card {
            background: #f8f9fa;
            color: #333;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid #e0e0e0;
        }
        .summary-card h3 {
            font-size: 1.2em;
            margin-bottom: 10px;
            color: #666;
        }
        .summary-card .value {
            font-size: 2.5em;
            font-weight: 700;
        }
        .legend {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .legend-color {
            width: 24px;
            height: 24px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏆 IVL联赛排名预测分析</h1>
        <div class="subtitle">基于蒙特卡洛模拟的100000次预测结果</div>
        
        <div class="card">
            <div class="legend">
                <div class="legend-item"><div class="legend-color group-winner"></div><span>胜者组</span></div>
                <div class="legend-item"><div class="legend-color group-a"></div><span>附加组A</span></div>
                <div class="legend-item"><div class="legend-color group-b"></div><span>附加组B</span></div>
                <div class="legend-item"><div class="legend-color group-eliminate"></div><span>淘汰</span></div>
            </div>
            <h2>📊 分组概率统计</h2>
            <table class="group-table">
                <thead>
                    <tr>
                        <th>队伍</th>
                        <th>胜者组<br></th>
                        <th>附加组A<br></th>
                        <th>附加组B<br></th>
                        <th>淘汰<br></th>
                        <th>平均位次</th>
                    </tr>
                </thead>
                <tbody>"""

    for t, i, avg_rank in team_data:
        winner_count = sum(all_res[i][0:4])
        a_count = sum(all_res[i][4:6])
        b_count = sum(all_res[i][6:8])
        eliminate_count = sum(all_res[i][8:10])
        winner_prob = winner_count / SIMULATION_COUNT * 100
        a_prob = a_count / SIMULATION_COUNT * 100
        b_prob = b_count / SIMULATION_COUNT * 100
        eliminate_prob = eliminate_count / SIMULATION_COUNT * 100

        html_content += f"""
                    <tr>
                        <td class="team-name">{t.upper()}</td>
                        <td>
                            <div class="bar-container">
                                <div class="bar group-winner" style="width:{winner_prob}%"></div>
                                <div class="bar-text prob-value">{format_prob(winner_count)}</div>
                            </div>
                        </td>
                        <td>
                            <div class="bar-container">
                                <div class="bar group-a" style="width:{a_prob}%"></div>
                                <div class="bar-text prob-value">{format_prob(a_count)}</div>
                            </div>
                        </td>
                        <td>
                            <div class="bar-container">
                                <div class="bar group-b" style="width:{b_prob}%"></div>
                                <div class="bar-text prob-value">{format_prob(b_count)}</div>
                            </div>
                        </td>
                        <td>
                            <div class="bar-container">
                                <div class="bar group-eliminate" style="width:{eliminate_prob}%"></div>
                                <div class="bar-text prob-value">{format_prob(eliminate_count)}</div>
                            </div>
                        </td>
                        <td class="avg-rank">{avg_rank:.2f}</td>
                    </tr>"""

    html_content += """
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>📈 详细排名概率分布</h2>
            <table class="rank-table">
                <thead>
                    <tr>
                        <th>名次</th>"""
    for t, i, avg_rank in team_data:
        html_content += f"""
                        <th>{t.upper()}</th>"""
    html_content += """
                    </tr>
                </thead>
                <tbody>"""

    rank_bar_classes = ['bar-gold', 'bar-silver', 'bar-bronze', 'bar-green', 'bar-sky', 'bar-sky', 'bar-purple', 'bar-purple', 'bar-red', 'bar-red']
    rank_labels = ['第1名', '第2名', '第3名', '第4名', '第5名', '第6名', '第7名', '第8名', '第9名', '第10名']

    for j in range(10):
        html_content += f"""
                    <tr>
                        <td class="team-name">{rank_labels[j]}</td>"""
        for t, i, avg_rank in team_data:
            count = all_res[i][j]
            prob = count / SIMULATION_COUNT * 100
            html_content += f"""
                        <td>
                            <div class="bar-container">
                                <div class="bar {rank_bar_classes[j]}" style="width:{prob}%"></div>
                                <div class="bar-text prob-value">{format_prob(count)}</div>
                            </div>
                        </td>"""
        html_content += """
                    </tr>"""

    html_content += """
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>📋 排名概率条形图</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px;">"""

    for t, i, avg_rank in team_data:
        html_content += f"""
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h3 style="text-align: center; margin-bottom: 15px; color: #667eea;">{t.upper()}</h3>"""
        for j in range(10):
            count = all_res[i][j]
            prob = count / SIMULATION_COUNT * 100
            rank_label = f'第{j+1}名'
            html_content += f"""
                    <div style="margin: 8px 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                            <span style="font-size: 0.9em;">{rank_label}</span>
                            <span class="prob-value" style="font-size: 0.9em;">{format_prob(count)}</span>
                        </div>
                        <div class="bar-container">
                            <div class="bar {rank_bar_classes[j]}" style="width:{prob}%"></div>
                        </div>
                    </div>"""
        html_content += """
                </div>"""

    html_content += """
            </div>
        </div>

        <div class="card">
            <h2>🎯 预测摘要</h2>
            <div class="summary-grid">"""

    html_content += f"""
                <div class="summary-card" style="grid-column: 1 / -1; text-align: center; padding: 30px;">
                    <h3 style="color: #333; margin-bottom: 20px;">📊 晋级分数线预测</h3>
                    <div style="display: flex; justify-content: center; gap: 60px; flex-wrap: wrap;">
                        <div style="color: #333;">
                            <div style="font-size: 1.2em; opacity: 0.7;">胜者组</div>
                            <div style="font-size: 3.5em; font-weight: 800; color: #4CAF50;">{winner_line:.2f}<span style="font-size: 0.5em;">胜</span></div>
                        </div>
                        <div style="color: #333;">
                            <div style="font-size: 1.2em; opacity: 0.7;">附加组A</div>
                            <div style="font-size: 3.5em; font-weight: 800; color: #FF9800;">{playoff_a_line:.2f}<span style="font-size: 0.5em;">胜</span></div>
                        </div>
                        <div style="color: #333;">
                            <div style="font-size: 1.2em; opacity: 0.7;">附加组B</div>
                            <div style="font-size: 3.5em; font-weight: 800; color: #2196F3;">{playoff_b_line:.2f}<span style="font-size: 0.5em;">胜</span></div>
                        </div>
                    </div>
                    <div style="color: #666; margin-top: 20px; font-size: 0.9em;">
                        * 分数线 = 相邻名次队伍胜场数的平均值
                    </div>
                </div>"""
    
    for t, i, avg_rank in team_data:
        most_likely_rank = all_res[i].index(max(all_res[i])) + 1
        current_wins = now_score[t][0]
        
        html_content += f"""
                <div class="summary-card">
                    <h3>{t.upper()}</h3>
                    <div style="font-size: 1.2em; margin-bottom: 5px;">当前胜场</div>
                    <div class="value" style="font-size: 2.5em;">{current_wins}</div>
                    <div style="margin-top: 10px; opacity: 0.9;">
                        平均位次: <strong>{avg_rank:.2f}</strong><br>
                        最可能名次: <strong>第{most_likely_rank}名</strong>
                    </div>
                </div>"""

    html_content += """
            </div>
        </div>

    </div>
</body>
</html>"""

    with open('ivl_prediction_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("HTML报告已生成: ivl_prediction_report.html")


for i, t in enumerate(teams):
    print(t, end=" ")
    print(format_prob(sum(all_res[i][0:4])), end=" ")
    print(format_prob(sum(all_res[i][4:6])), end=" ")
    print(format_prob(sum(all_res[i][6:8])), end=" ")
    print(format_prob(sum(all_res[i][8:10])), end=" ")
    ax = 0
    for j, p in enumerate(all_res[i]):
        ax += p * (j + 1)
    print("{:.2f}".format(ax / SIMULATION_COUNT))
    for j in all_res[i]:
        print(format_prob(j), sep="", end=" ")
    print("")

generate_html_report(all_res, teams, winner_line, playoff_a_line, playoff_b_line)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"\n计算用时: {elapsed_time:.2f} 秒")