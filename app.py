
from flask import Flask, render_template, request
from strategy import decide, feedback
from scoring import score
from roads.engine import compute_all

app = Flask(__name__)

results = []
history = []
total = 0
last = None

@app.route("/", methods=["GET", "POST"])
def index():
    global results, history, total, last

    if request.method == "POST":
        a = request.form.get("act")
        if a in ("B", "P", "T"):
            if last and last["act"] != "NO":
                s = score(last["conf"], a == last["act"])
                total += s
                history.append((last["act"], last["conf"], s))
                feedback(a, last["preds"])
            results.append(a)

        elif a == "UNDO" and results:
            results.pop()

        elif a == "RESET":
            results.clear()
            history.clear()
            total = 0

    act, conf, preds = decide(results)
    last = {"act": act, "conf": conf, "preds": preds}

    # ===== 連勝 / 連敗計算 =====
    streak_type = None
    streak_len = 0
    for _a, _c, _s in reversed(history):
        if _s == 0:
            continue
        cur = "W" if _s > 0 else "L"
        if streak_type is None:
            streak_type = cur
            streak_len = 1
        elif cur == streak_type:
            streak_len += 1
        else:
            break

    roads = compute_all(results)

    return render_template(
        "index.html",
        act=act,
        conf=conf,
        total=total,
        hist=history,
        roads=roads,
        streak_type=streak_type,
        streak_len=streak_len,
    )

if __name__ == "__main__":
    app.run(debug=True)
