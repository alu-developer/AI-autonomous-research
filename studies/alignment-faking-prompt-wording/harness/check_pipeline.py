"""Pipeline checks registered in v1.1: (1) simulated data with NO fragility and NO cue specificity: the rate of false
'supported' verdicts for H1 and H3 must be at most 5%; (2) label-permuted pilot data: the interval for the anchor gap
must exclude 0 in at most about 5% of permutations. Uses the exact analysis functions of analysis.py.
  python harness/check_pipeline.py [N_SIMS] [B]
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analysis as A
import common as C

N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
B = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
Q, P, R, NC, NPL = 40, 23, 4, 7, 10
rng = np.random.default_rng(5)
expit = lambda x: 1 / (1 + np.exp(-x)); logit = lambda p: np.log(p / (1 - p))
summ = json.load(open(os.path.join(HERE, "..", "data", "design_choice.json")))["models"]

def sim_calls(m):
    a_f, a_p, qsd = logit(summ[m]["free"]), logit(summ[m]["paid"]), summ[m]["qsd"]
    u = rng.normal(0, qsd, Q); pa = rng.normal(0, 0.5, P + NC + NPL)
    calls = []
    def add(pid, idx, reps):
        for q in range(Q):
            for tier, a in (("free", a_f), ("paid", a_p)):
                for _ in range(reps):
                    calls.append({"q": q, "prompt": pid, "tier": tier, "y": int(rng.random() < expit(a + u[q] + idx))})
    add("anchor", 0.0, R); add("anchor_placebo", 0.0, 1)
    for i in range(P): add(f"p{i}", pa[i], 1)
    for i in range(NC): add(f"c{i}", pa[P + i], 1)
    for i in range(NPL):
        add(f"x{i}", pa[P + NC + i], 1); add(f"placebo_x{i}", pa[P + NC + i], 1)   # placebo behaves like the real cue: no specificity
    return calls

out = {}
for m in summ:
    sup1 = sup3 = 0
    for _ in range(N):
        calls = sim_calls(m)
        # the 10 real-cue prompts x_i are separate ids; pair them with their placebo versions
        pairs = [("anchor", "anchor_placebo")] + [(f"x{i}", f"placebo_x{i}") for i in range(NPL)]
        r = A.analyze_model(calls, Q, "anchor", [f"p{i}" for i in range(P)], [f"c{i}" for i in range(NC)], pairs, B=B)
        sup1 += r["H1"]["verdict"] == "supported"; sup3 += r["H3"]["verdict"] == "supported"
    out[m] = {"false_supported_H1": sup1 / N, "false_supported_H3": sup3 / N}
    print(m, out[m], flush=True)

# label-permuted pilot
raw = {}
for l in open(os.path.join(HERE, "..", "data", "pilot_raw.jsonl")):
    r = json.loads(l)
    if r["cell"] not in raw or r["attempt"] > raw[r["cell"]]["attempt"]: raw[r["cell"]] = r
clf = {}
for l in open(os.path.join(HERE, "..", "data", "pilot_clf.jsonl")):
    r = json.loads(l); clf[r["id"]] = r
for m in summ:
    cs = [(r["q"], r["tier"], C.comply(clf[c + "|A"]["label"])) for c, r in raw.items()
          if r["model"] == m and r["parsed"] and (clf.get(c + "|A") or {}).get("label")]
    excl = 0; NP = 300
    for _ in range(NP):
        tiers = [t for _, t, _ in cs]; rng.shuffle(tiers)
        F = {}; Pd = {}
        for (q, _, y), t in zip(cs, tiers): (F if t == "free" else Pd).setdefault(q, []).append(y)
        g = np.array([np.mean(F.get(q, [np.nan])) - np.mean(Pd.get(q, [np.nan])) for q in range(12)])
        boots = [np.nanmean(g[rng.integers(0, 12, 12)]) for _ in range(500)]
        lo, hi = np.quantile(boots, [0.0125, 0.9875]); excl += (lo > 0 or hi < 0)
    out[m]["permuted_pilot_ci_excludes_0"] = excl / NP
    print(m, "permuted pilot CI excludes 0:", excl / NP, flush=True)
json.dump(out, open(os.path.join(HERE, "..", "results_pipeline_check.json"), "w"), indent=1)
