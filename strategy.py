
from collections import defaultdict, Counter, deque

HIST=20
perf={k:deque(maxlen=HIST) for k in ("freq","markov","streak")}

def _clean(r):
    return [x for x in r if x in ("B","P")]

def freq(r):
    s=_clean(r)
    return "B" if not s or s.count("B")>=s.count("P") else "P"

def markov2(r):
    s=_clean(r)
    if len(s)<3: return "B"
    t=defaultdict(Counter)
    for i in range(len(s)-2):
        t[(s[i],s[i+1])][s[i+2]]+=1
    c=t.get((s[-2],s[-1]))
    return "B" if not c or c["B"]>=c["P"] else "P"

def streak(r):
    s=_clean(r)
    if len(s)<2: return "B"
    # simple "反轉傾向": 若連兩手同方，預測反向，否則預測莊(基準)
    return ("P" if s[-1]=="B" else "B") if s[-1]==s[-2] else "B"

def w(k):
    h=perf[k]
    return sum(h)/len(h) if h else 1.0

def decide(r):
    s=_clean(r)
    # 第一局(尚無莊閒結果)不給預測
    if len(s) == 0:
        return "NO", 0, {"freq":"B","markov":"B","streak":"B"}

    preds={"freq":freq(r),"markov":markov2(r),"streak":streak(r)}

    # 用加權投票轉成機率，再轉成 10 的倍數
    sb = (w("freq") if preds["freq"]=="B" else 0.0) + (w("markov") if preds["markov"]=="B" else 0.0) + (w("streak") if preds["streak"]=="B" else 0.0)
    sp = (w("freq") if preds["freq"]=="P" else 0.0) + (w("markov") if preds["markov"]=="P" else 0.0) + (w("streak") if preds["streak"]=="P" else 0.0)
    tot = sb + sp if (sb+sp)>0 else 1.0
    pB = sb / tot
    margin = abs(pB - 0.5)  # 0..0.5

    # 把 margin 映射到 50..90（更保守，不會每局 90）
    raw = 50 + int(margin * 80) * 10  # margin=0 ->50, margin=0.5 -> 90
    conf = max(50, min(90, (raw//10)*10))

    # 小樣本更保守：前 6 手封頂 70
    if len(s) < 6:
        conf = min(conf, 70)

    act = "B" if pB >= 0.5 else "P"
    # 若信心只是 50，視為不下注（製造分別）
    if conf <= 50:
        return "NO", 50, preds

    return act, conf, preds

def feedback(actual, preds):
    for k,v in preds.items():
        perf[k].append(1 if v==actual else 0)
