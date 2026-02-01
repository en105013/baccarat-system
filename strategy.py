
from collections import defaultdict, Counter, deque

HIST = 30
perf = {k: deque(maxlen=HIST) for k in ("freq", "markov", "streak")}

def _clean(r):
    return [x for x in r if x in ("B", "P")]

def freq(r):
    s = _clean(r)
    if not s:
        return "B"
    return "B" if s.count("B") >= s.count("P") else "P"

def markov2(r):
    s = _clean(r)
    if len(s) < 3:
        return "B"
    t = defaultdict(Counter)
    for i in range(len(s) - 2):
        t[(s[i], s[i + 1])][s[i + 2]] += 1
    c = t.get((s[-2], s[-1]))
    return "B" if not c or c["B"] >= c["P"] else "P"

def streak(r):
    s = _clean(r)
    if len(s) < 2:
        return "B"
    # 連兩手同方：偏向反轉；否則偏向延續上一手
    if s[-1] == s[-2]:
        return "P" if s[-1] == "B" else "B"
    return s[-1]

def w(k):
    h = perf[k]
    return sum(h) / len(h) if h else 0.55  # 沒資料時中性略偏

def _round5(x: float) -> int:
    return int(round(x / 5.0) * 5)

def decide(r):
    s = _clean(r)

    # 第一局不預測
    if len(s) == 0:
        return "NO", 0, {"freq": "B", "markov": "B", "streak": "B"}

    preds = {"freq": freq(r), "markov": markov2(r), "streak": streak(r)}

    # 加權投票 -> 機率
    sb = (w("freq") if preds["freq"] == "B" else 0.0) + (w("markov") if preds["markov"] == "B" else 0.0) + (w("streak") if preds["streak"] == "B" else 0.0)
    sp = (w("freq") if preds["freq"] == "P" else 0.0) + (w("markov") if preds["markov"] == "P" else 0.0) + (w("streak") if preds["streak"] == "P" else 0.0)
    tot = sb + sp if (sb + sp) > 0 else 1.0
    pB = sb / tot
    margin = abs(pB - 0.5)  # 0..0.5

    # ===== 信心值（更有起伏、更保守）=====
    # 基礎：45..80（不會動不動 90）
    base = 45 + (margin * 70)  # margin=0 ->45, margin=0.5 ->80

    # 小樣本保守：前期壓縮幅度，慢慢放寬
    n = len(s)
    sample_factor = min(1.0, n / 20.0)  # 0..1
    base = 45 + (base - 45) * (0.55 + 0.45 * sample_factor)

    # 近期表現校正：命中率偏低下調、偏高小幅上調
    recent = []
    for k in ("freq", "markov", "streak"):
        if perf[k]:
            recent.append(sum(perf[k]) / len(perf[k]))
    recent_acc = sum(recent) / len(recent) if recent else 0.55
    base += (recent_acc - 0.55) * 25  # 約 -10..+10

    conf = _round5(max(40, min(85, base)))

    act = "B" if pB >= 0.5 else "P"

    # 狀態不清楚 -> 觀望（不下注）
    if conf <= 45:
        return "NO", conf, preds

    return act, conf, preds

def feedback(actual, preds):
    for k, v in preds.items():
        perf[k].append(1 if v == actual else 0)
