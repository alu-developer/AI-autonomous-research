"""Post-pilot design rule (amendment-1, section 7). Reads pilot data, simulates H1 power per grid design, picks a design.

  python harness/design_rule.py MODEL_A MODEL_B [--spent USD]

Inputs: data/pilot_raw.jsonl, data/pilot_clf.jsonl, data/pilot_summary.json (measured costs), data/ledger.jsonl.
Fixed settings (registered): paraphrase SD 0.5 (logit), query SD from pilot moments clipped to [0.5, 1.5], scenario
D = 0.6 x pilot gap, 97.5% percentile bootstrap (300 resamples), 200 simulated studies per design and model, seed 11,
power target 0.80, projected-usage limit 40.0 USD.
"""
import json
import os
import sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
sys.path.insert(0, HERE)
import common as C

GRID = {  # name: (Q, P, R, Cc)
    "G1": (12, 23, 4, 7), "G2": (20, 23, 4, 7), "G3": (40, 23, 4, 7),
    "G4": (80, 23, 4, 7), "G5": (40, 46, 8, 10), "G6": (80, 46, 8, 10),
}
PLACEBO_PROMPTS = 11
LIMIT_USD = 40.0
EXTRA_PER_PAIR = 0.0003   # classifier A, 25% B, scratchpad votes: upper estimate per paired call (registered below in amendment-1)
PSD = 0.5
rng = np.random.default_rng(11)
expit = lambda x: 1 / (1 + np.exp(-x))
logit = lambda p: np.log(p / (1 - p))


def pilot_cells(model):
    raw = {}
    for l in open(os.path.join(DATA, "pilot_raw.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        if r["model"] == model and (r["cell"] not in raw or r["attempt"] > raw[r["cell"]]["attempt"]):
            raw[r["cell"]] = r
    clf = {}
    for l in open(os.path.join(DATA, "pilot_clf.jsonl"), encoding="utf-8"):
        r = json.loads(l)
        clf[r["id"]] = r
    out = []
    for cell, r in raw.items():
        lab = (clf.get(cell + "|A") or {}).get("label")
        if r["parsed"] and lab:
            out.append((r["q"], r["tier"], C.comply(lab)))
    return out


def query_sd(cells):
    qs = {}
    for q, t, y in cells:
        qs.setdefault(q, []).append(y)
    rates = np.array([np.mean(v) for v in qs.values()])
    ns = np.array([len(v) for v in qs.values()])
    rates = np.clip(rates, 0.05, 0.95)
    lg = logit(rates)
    noise = np.mean(1 / (ns * rates * (1 - rates)))
    sd = np.sqrt(max(np.var(lg, ddof=1) - noise, 0.0))
    return float(np.clip(sd, 0.5, 1.5))


def simulate_once(Q, P, R, a_paid, a_free, s_p, qsd):
    u = rng.normal(0, qsd, Q)
    pa = rng.normal(0, PSD, P)
    A = (rng.random((R, Q)) < expit(a_free + u)).astype(float) - (rng.random((R, Q)) < expit(a_paid + u))
    Pm = (rng.random((P, Q)) < expit(a_free + s_p + pa[:, None] + u[None, :])).astype(float) \
        - (rng.random((P, Q)) < expit(a_paid + pa[:, None] + u[None, :]))
    return A, Pm


def lower_bound(A, Pm, B=300, level=0.975):
    R, Q = A.shape
    P = Pm.shape[0]
    qi = rng.integers(0, Q, (B, Q))
    pi = rng.integers(0, P, (B, P))
    D = np.empty(B)
    for b in range(B):
        D[b] = A[:, qi[b]].mean() - Pm[np.ix_(pi[b], qi[b])].mean()
    return np.quantile(D, (1 - level) / 2)


def solve_shift(a_paid, a_free, target_gap, qsd):
    """Find the free-tier logit shift s_p so that the mean gap over paraphrase and query draws equals target_gap."""
    u = rng.normal(0, qsd, 20000)
    pa = rng.normal(0, PSD, 20000)
    lo, hi = -8.0, 8.0
    for _ in range(40):
        mid = (lo + hi) / 2
        g = (expit(a_free + mid + pa + u) - expit(a_paid + pa + u)).mean()
        if g > target_gap:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def power(Q, P, R, a_paid, a_free, s_p, qsd, N=200):
    return float(np.mean([lower_bound(*simulate_once(Q, P, R, a_paid, a_free, s_p, qsd)) > 0 for _ in range(N)]))


def main(models, spent):
    summ = json.load(open(os.path.join(DATA, "pilot_summary.json")))["models"]
    per_model = {}
    for m in models:
        cells = pilot_cells(m)
        free = np.mean([y for q, t, y in cells if t == "free"])
        paid = np.mean([y for q, t, y in cells if t == "paid"])
        pf, pp = float(np.clip(free, 0.02, 0.98)), float(np.clip(paid, 0.02, 0.98))
        g = pf - pp
        qsd = query_sd(cells)
        a_paid, a_free = logit(pp), logit(pf)
        s_p = solve_shift(a_paid, a_free, 0.4 * g, qsd)   # paraphrase gap = 0.4 x pilot gap, so D = 0.6 x gap
        per_model[m] = {"free": pf, "paid": pp, "gap": g, "qsd": qsd, "s_p": s_p, "cost_pair": summ[m]["cost_per_paired_call_usd"]}
    rows = []
    for name, (Q, P, R, Cc) in GRID.items():
        pair_units = Q * (R + P + Cc + PLACEBO_PROMPTS)  # paired calls per model
        cost = spent + sum(pair_units * (per_model[m]["cost_pair"] + EXTRA_PER_PAIR) for m in models)
        pw = {m: power(Q, P, R, logit(per_model[m]["paid"]), logit(per_model[m]["free"]), per_model[m]["s_p"], per_model[m]["qsd"])
              for m in models}
        rows.append({"design": name, "Q": Q, "P": P, "R": R, "C": Cc, "paired_calls_per_model": pair_units,
                     "projected_total_usd": round(cost, 2), "fits": cost <= LIMIT_USD, "power": pw,
                     "min_power": min(pw.values())})
        print(rows[-1], flush=True)
    fit = [r for r in rows if r["fits"]]
    ok = [r for r in fit if r["min_power"] >= 0.80]
    if ok:
        pick = min(ok, key=lambda r: r["projected_total_usd"])
        verdict = "cheapest design with min power >= 0.80 that fits"
    elif fit:
        pick = max(fit, key=lambda r: (r["min_power"], -r["projected_total_usd"]))
        verdict = "no design reaches 0.80 within the limit: highest min power that fits; results labeled underpowered"
    else:
        pick, verdict = None, "no design fits: stop and ask the author"
    out = {"models": per_model, "spent_before_main_usd": spent, "grid": rows, "pick": pick, "rule_result": verdict}
    json.dump(out, open(os.path.join(DATA, "design_choice.json"), "w"), indent=1)
    print("PICK:", pick["design"] if pick else None, "|", verdict)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    spent = 0.0
    if "--spent" in sys.argv:
        spent = float(sys.argv[sys.argv.index("--spent") + 1])
        args = [a for a in args if a != str(spent)]
    main(args, spent)
