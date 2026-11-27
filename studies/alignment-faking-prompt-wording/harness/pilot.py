"""Pilot runner: 8 candidates x (5 samples x first 12 queries x 2 tiers) = 960 calls, anchor prompt only.

Usage (all resumable; each invocation stops by itself after --seconds):
  python harness/pilot.py run --seconds 150 [--cap 5.0]
  python harness/pilot.py classify --seconds 150
  python harness/pilot.py summarize
Raw outputs go to data/pilot_raw.jsonl, classifier outputs to data/pilot_clf.jsonl.
The key is read from .env by or_client and never printed.
"""
import argparse
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from or_client import Client, SpendCapReached
import common as C

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA = os.path.join(ROOT, "data")
MAT = os.path.join(ROOT, "materials")
RAW = os.path.join(DATA, "pilot_raw.jsonl")
CLF = os.path.join(DATA, "pilot_clf.jsonl")
LEDGER = os.path.join(DATA, "ledger.jsonl")
SEED = 20261127
NQ, NREP = 12, 5

anchor = open(os.path.join(MAT, "anchor_system.txt"), encoding="utf-8").read().strip()
queries = json.load(open(os.path.join(MAT, "queries.json"), encoding="utf-8"))[:NQ]


def cells():
    """All pilot cells in registered order: query by query; within a query, models x reps x tiers shuffled."""
    rng = random.Random(SEED)
    out = []
    for qi in range(NQ):
        block = [(m, qi, rep, tier) for m in C.SUBJECT_CANDIDATES for rep in range(NREP) for tier in (True, False)]
        rng.shuffle(block)
        out += block
    return out


def key(m, qi, rep, tier):
    return f"{m}|q{qi}|r{rep}|{'free' if tier else 'paid'}"


def done_keys(path, field="cell"):
    s = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                r = json.loads(line)
                s[r[field]] = r
    return s


def call_cell(client, cell, attempt):
    m, qi, rep, tier = cell
    msgs = [{"role": "system", "content": anchor}, {"role": "user", "content": C.user_turn(queries[qi], tier)}]
    r = client.chat(m, msgs, max_tokens=4000, temperature=1.0, tag=f"pilot|{key(*cell)}|a{attempt}",
                    extra=C.reasoning_extra(m), provider=C.PROVIDER_PIN[m])
    ans = C.final_answer(r["text"])
    return {"cell": key(*cell), "model": m, "q": qi, "rep": rep, "tier": "free" if tier else "paid", "attempt": attempt,
            "provider": r["provider"], "finish": r["finish_reason"], "cost_usd": r["cost_usd"],
            "ptok": r["prompt_tokens"], "ctok": r["completion_tokens"], "rtok": r["reasoning_tokens"],
            "error": r["error"], "text": r["text"], "parsed": ans is not None and r["error"] is None and r["finish_reason"] != "length"}


def run(seconds, cap):
    client = Client(os.path.join(DATA, "pilot_client_raw.jsonl"), LEDGER, cap_usd=cap)
    have = done_keys(RAW)
    todo = [c for c in cells() if key(*c) not in have]
    print("todo", len(todo), "done", len(have), "spent", round(client.spent(), 4), flush=True)
    t0 = time.time()
    stop = False
    with ThreadPoolExecutor(12) as ex, open(RAW, "a", encoding="utf-8") as out:
        it = iter(todo)
        futs = set()

        def submit_next():
            try:
                c = next(it)
            except StopIteration:
                return False
            futs.add(ex.submit(call_cell, client, c, 0))
            return True
        for _ in range(12):
            submit_next()
        while futs:
            for f in as_completed(list(futs)):
                futs.discard(f)
                try:
                    rec = f.result()
                except SpendCapReached as e:
                    print("SPEND CAP:", e, flush=True)
                    stop = True
                    continue
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
                if not stop and time.time() - t0 < seconds:
                    submit_next()
                break
    print("batch done; spent", round(client.spent(), 4), flush=True)


def retry_failed(cap):
    """Registered rule: truncated or unparseable outputs are retried once."""
    client = Client(os.path.join(DATA, "pilot_client_raw.jsonl"), LEDGER, cap_usd=cap)
    rows = [json.loads(l) for l in open(RAW, encoding="utf-8") if l.strip()]
    first = {r["cell"]: r for r in rows if r["attempt"] == 0}
    retried = {r["cell"] for r in rows if r["attempt"] == 1}
    bad = [r for r in first.values() if not r["parsed"] and r["cell"] not in retried]
    print("retrying", len(bad), flush=True)
    with ThreadPoolExecutor(8) as ex, open(RAW, "a", encoding="utf-8") as out:
        futs = []
        for r in bad:
            m, q, rep, tier = r["model"], r["q"], r["rep"], r["tier"] == "free"
            futs.append(ex.submit(call_cell, client, (m, q, rep, tier), 1))
        for f in futs:
            try:
                out.write(json.dumps(f.result(), ensure_ascii=False) + "\n")
            except SpendCapReached as e:
                print("SPEND CAP:", e)
                break


def final_rows():
    """One row per cell: retry result if the first attempt failed to parse, else the first attempt."""
    rows = [json.loads(l) for l in open(RAW, encoding="utf-8") if l.strip()]
    by = {}
    for r in rows:
        if r["cell"] not in by or r["attempt"] > by[r["cell"]]["attempt"]:
            by[r["cell"]] = r
    return by


def classify(seconds, cap):
    client = Client(os.path.join(DATA, "pilot_clf_client_raw.jsonl"), LEDGER, cap_usd=cap)
    rows = final_rows()
    have = done_keys(CLF, "id")
    rng = random.Random(SEED + 1)
    jobs = []
    for cell, r in sorted(rows.items()):
        if not r["parsed"]:
            continue
        ans = C.final_answer(r["text"])
        qtext = queries[r["q"]]
        jobs.append((cell + "|A", C.CLASSIFIER_A, qtext, ans))
        if rng.random() < 0.25:
            jobs.append((cell + "|B", C.CLASSIFIER_B, qtext, ans))
    jobs = [j for j in jobs if j[0] not in have]
    print("classify todo", len(jobs), flush=True)
    t0 = time.time()

    def one(j):
        jid, model, q, ans = j
        r = client.chat(model, [{"role": "user", "content": C.CLASSIFIER_PROMPT.format(query=q, answer=ans)}],
                        max_tokens=300, temperature=0.0, tag=f"clf|{jid}", extra=C.reasoning_extra(model),
                        provider=C.PROVIDER_PIN[model])
        lab = (C.jload(r["text"]) or {}).get("label")
        return {"id": jid, "model": model, "label": lab if lab in C.LABELS else None, "cost_usd": r["cost_usd"],
                "error": r["error"]}
    with ThreadPoolExecutor(12) as ex, open(CLF, "a", encoding="utf-8") as out:
        it = iter(jobs)
        futs = set()
        for _ in range(12):
            try:
                futs.add(ex.submit(one, next(it)))
            except StopIteration:
                break
        while futs:
            for f in as_completed(list(futs)):
                futs.discard(f)
                try:
                    out.write(json.dumps(f.result()) + "\n")
                    out.flush()
                except SpendCapReached as e:
                    print("SPEND CAP:", e)
                    continue
                if time.time() - t0 < seconds:
                    try:
                        futs.add(ex.submit(one, next(it)))
                    except StopIteration:
                        pass
                break
    print("classify batch done; spent", round(client.spent(), 4), flush=True)


def repair(cap):
    """Amendment 2: for A/B jobs without a valid label, re-ask once with the digit-format prompt (network errors: same prompt)."""
    client = Client(os.path.join(DATA, "pilot_clf_client_raw.jsonl"), LEDGER, cap_usd=cap)
    rows = final_rows()
    have = done_keys(CLF, "id")
    todo = [jid for jid, r in have.items() if r["label"] is None and not r.get("repaired")]
    print("repair todo", len(todo), flush=True)

    def one(jid):
        cell, which = jid.rsplit("|", 1)
        r = rows[cell]
        model = C.CLASSIFIER_A if which == "A" else C.CLASSIFIER_B
        q, ans = queries[r["q"]], C.final_answer(r["text"])
        res = client.chat(model, [{"role": "user", "content": C.CLASSIFIER_PROMPT_DIGITS.format(query=q, answer=ans)}],
                          max_tokens=300, temperature=0.0, tag=f"clf_repair|{jid}", extra=C.reasoning_extra(model),
                          provider=C.PROVIDER_PIN[model])
        return {"id": jid, "model": model, "label": C.parse_digit_label(res["text"]), "cost_usd": res["cost_usd"],
                "error": res["error"], "repaired": True}
    with ThreadPoolExecutor(12) as ex:
        new = list(ex.map(one, todo))
    # rewrite CLF with repaired rows replacing the originals (originals kept in pilot_clf_client_raw.jsonl)
    out = dict(have)
    for r in new:
        out[r["id"]] = r
    with open(CLF, "w", encoding="utf-8") as f:
        for r in out.values():
            f.write(json.dumps(r) + "\n")
    print("repaired; still missing:", sum(1 for r in new if r["label"] is None), flush=True)


def summarize():
    rows = final_rows()
    clf = done_keys(CLF, "id")
    res = {}
    for m in C.SUBJECT_CANDIDATES:
        d = {"free": [], "paid": []}
        cost, n, miss = 0.0, 0, {"free": 0, "paid": 0}
        flagged = {"free": 0, "paid": 0}
        provs = set()
        ctoks = []
        for cell, r in rows.items():
            if r["model"] != m:
                continue
            n += 1
            cost += r["cost_usd"] or 0.0
            provs.add(r["provider"])
            ctoks.append(r["ctok"] or 0)
            if not r["parsed"]:
                miss[r["tier"]] += 1
                continue
            lab = (clf.get(cell + "|A") or {}).get("label")
            if lab is None:
                miss[r["tier"]] += 1
                continue
            d[r["tier"]].append(C.comply(lab))
            if C.mentions_tier_or_training(C.final_answer(r["text"])):
                flagged[r["tier"]] += 1
        pf = sum(d["free"]) / len(d["free"]) if d["free"] else None
        pp = sum(d["paid"]) / len(d["paid"]) if d["paid"] else None
        res[m] = {"n_calls": n, "free_rate": pf, "paid_rate": pp,
                  "gap": None if pf is None or pp is None else pf - pp,
                  "n_free": len(d["free"]), "n_paid": len(d["paid"]), "missing": miss, "regex_flagged": flagged,
                  "cost_usd_subject_calls": round(cost, 4), "cost_per_paired_call_usd": round(2 * cost / n, 6) if n else None,
                  "mean_completion_tokens": round(sum(ctoks) / len(ctoks), 1) if ctoks else None,
                  "providers": sorted(p for p in provs if p)}
    # agreement of classifier B with A on the audited subset
    both = {}
    for jid, r in clf.items():
        if jid.endswith("|B") and r["label"]:
            a = clf.get(jid[:-1] + "A")
            if a and a["label"]:
                both[jid[:-2]] = (C.comply(a["label"]), C.comply(r["label"]))
    n = len(both)
    if n:
        po = sum(1 for a, b in both.values() if a == b) / n
        pa = sum(a for a, _ in both.values()) / n
        pb = sum(b for _, b in both.values()) / n
        pe = pa * pb + (1 - pa) * (1 - pb)
        kappa = (po - pe) / (1 - pe) if pe < 1 else None
    else:
        po = kappa = None
    out = {"models": res, "classifier_agreement": {"n": n, "observed": po, "kappa": kappa}}
    json.dump(out, open(os.path.join(DATA, "pilot_summary.json"), "w"), indent=1)
    for m, d in res.items():
        print(f"{m:40s} free={d['free_rate']} paid={d['paid_rate']} gap={d['gap']} n={d['n_free']}/{d['n_paid']} "
              f"miss={d['missing']} $pair={d['cost_per_paired_call_usd']} tok={d['mean_completion_tokens']}")
    print("agreement", out["classifier_agreement"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "retry", "classify", "repair", "summarize"])
    ap.add_argument("--seconds", type=float, default=150)
    ap.add_argument("--cap", type=float, default=5.0)
    a = ap.parse_args()
    {"run": lambda: run(a.seconds, a.cap), "retry": lambda: retry_failed(a.cap),
     "classify": lambda: classify(a.seconds, a.cap), "repair": lambda: repair(a.cap),
     "summarize": summarize}[a.cmd]()
