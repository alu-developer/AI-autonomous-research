"""Main run, design G3 (amendment 3): Q=40, 23 primary paraphrases, 4 anchor reps, 7 compressed, 11 placebo prompts, 2 tiers.

  python harness/main_run.py run --seconds 150     # subject calls, resumable, query by query
  python harness/main_run.py retry                 # unparseable/truncated outputs, once
  python harness/main_run.py classify --seconds 150  # classifier A on all, B on a seeded 25%; invalid labels repaired once
  python harness/main_run.py summary               # counts, spend

Raw outputs: data/main_raw.jsonl ; labels: data/main_clf.jsonl ; API-level logs: data/main_*_client_raw.jsonl
"""
import argparse
import hashlib
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
RAW = os.path.join(DATA, "main_raw.jsonl")
CLF = os.path.join(DATA, "main_clf.jsonl")
LEDGER = os.path.join(DATA, "ledger.jsonl")
MODELS = ["google/gemini-3.1-flash-lite", "qwen/qwen3.8-27b"]
Q, NANCHOR = 40, 4
PRIMARY_COUNTS = {"lexical": 8, "structural": 8, "register": 7}
N_COMPRESSED = 7
N_PLACEBO_PARA = 10
SEED = 20261127
MATERIALS_HASH = open(os.path.join(MAT, "MATERIALS_HASH.txt")).read().strip()
USAGE_CAP = 42.0

anchor = open(os.path.join(MAT, "anchor_system.txt"), encoding="utf-8").read().strip()
anchor_placebo = open(os.path.join(MAT, "anchor_placebo_system.txt"), encoding="utf-8").read().strip()
queries = json.load(open(os.path.join(MAT, "queries.json"), encoding="utf-8"))[:Q]
paras = json.load(open(os.path.join(MAT, "paraphrases.json"), encoding="utf-8"))
placebo = json.load(open(os.path.join(MAT, "placebo_paraphrases.json"), encoding="utf-8"))

primary = []
for stratum, n in PRIMARY_COUNTS.items():
    primary += paras[stratum][:n]
compressed = paras["compressed"][:N_COMPRESSED]
TEXT = {"anchor": anchor, "anchor_placebo": anchor_placebo}
for p in primary + compressed:
    TEXT[p["id"]] = p["text"]
_elig = sorted(p["id"] for p in primary if placebo.get(p["id"], {}).get("ok"))
PLACEBO_IDS = random.Random(int(MATERIALS_HASH[:8], 16)).sample(_elig, N_PLACEBO_PARA)
for pid in PLACEBO_IDS:
    TEXT["placebo_" + pid] = placebo[pid]["text"]

# prompt specs: (prompt_id, kind, reps)
PROMPTS = [("anchor", "anchor", NANCHOR)]
PROMPTS += [(p["id"], "para", 1) for p in primary]
PROMPTS += [(p["id"], "comp", 1) for p in compressed]
PROMPTS += [("anchor_placebo", "placebo", 1)] + [("placebo_" + pid, "placebo", 1) for pid in PLACEBO_IDS]


def cells():
    rng = random.Random(SEED)
    out = []
    for qi in range(Q):
        block = []
        for m in MODELS:
            for pid, kind, reps in PROMPTS:
                for rep in range(reps):
                    for tier in (True, False):
                        block.append((m, qi, pid, rep, tier))
        rng.shuffle(block)
        out += block
    return out


def key(m, qi, pid, rep, tier):
    return f"{m}|q{qi}|{pid}|r{rep}|{'free' if tier else 'paid'}"


def kind_of(pid):
    for p, k, _ in PROMPTS:
        if p == pid:
            return k


def load(path, field):
    d = {}
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                r = json.loads(line)
                if field not in r:
                    continue
                if r[field] not in d or r.get("attempt", 0) >= d[r[field]].get("attempt", 0):
                    d[r[field]] = r
    return d


def call_cell(client, cell, attempt):
    m, qi, pid, rep, tier = cell
    msgs = [{"role": "system", "content": TEXT[pid]}, {"role": "user", "content": C.user_turn(queries[qi], tier)}]
    r = client.chat(m, msgs, max_tokens=4000, temperature=1.0, tag=f"main|{key(*cell)}|a{attempt}",
                    extra=C.reasoning_extra(m), provider=C.PROVIDER_PIN[m])
    ans = C.final_answer(r["text"])
    return {"cell": key(*cell), "model": m, "q": qi, "prompt": pid, "kind": kind_of(pid), "rep": rep,
            "tier": "free" if tier else "paid", "attempt": attempt, "provider": r["provider"],
            "finish": r["finish_reason"], "cost_usd": r["cost_usd"], "ptok": r["prompt_tokens"], "ctok": r["completion_tokens"],
            "error": r["error"], "text": r["text"],
            "parsed": ans is not None and r["error"] is None and r["finish_reason"] != "length",
            "req_hash": hashlib.sha256(json.dumps(msgs).encode()).hexdigest()[:16]}


def pool_run(fn, items, seconds, workers=int(os.environ.get("WORKERS", "16")), out_path=None):
    t0 = time.time()
    it = iter(items)
    futs = set()
    n = 0
    with ThreadPoolExecutor(workers) as ex, open(out_path, "a", encoding="utf-8") as out:
        def nxt():
            try:
                futs.add(ex.submit(fn, next(it)))
            except StopIteration:
                pass
        for _ in range(workers):
            nxt()
        while futs:
            for f in as_completed(list(futs)):
                futs.discard(f)
                try:
                    out.write(json.dumps(f.result(), ensure_ascii=False) + "\n")
                    out.flush()
                    n += 1
                except SpendCapReached as e:
                    print("SPEND CAP:", e, flush=True)
                    seconds = 0
                except Exception as e:  # keep the batch alive; the cell stays undone
                    print("ERR", type(e).__name__, str(e)[:120], flush=True)
                if time.time() - t0 < seconds:
                    nxt()
                break
    return n


def run(seconds):
    client = Client(os.path.join(DATA, "main_client_raw.jsonl"), LEDGER, cap_usd=USAGE_CAP)
    have = load(RAW, "cell")
    todo = [c for c in cells() if key(*c) not in have]
    print("todo", len(todo), "done", len(have), "spent", round(client.spent(), 3), flush=True)
    n = pool_run(lambda c: call_cell(client, c, 0), todo, seconds, out_path=RAW)
    print("batch calls", n, "spent", round(client.spent(), 3), flush=True)


def retry():
    client = Client(os.path.join(DATA, "main_client_raw.jsonl"), LEDGER, cap_usd=USAGE_CAP)
    rows = [json.loads(l) for l in open(RAW, encoding="utf-8") if l.strip()]
    first = {r["cell"]: r for r in rows if r["attempt"] == 0}
    retried = {r["cell"] for r in rows if r["attempt"] == 1}
    bad = [r for r in first.values() if not r["parsed"] and r["cell"] not in retried]
    print("retrying", len(bad), flush=True)
    items = [(r["model"], r["q"], r["prompt"], r["rep"], r["tier"] == "free") for r in bad]
    pool_run(lambda c: call_cell(client, c, 1), items, 1e9, out_path=RAW)


def final_rows():
    return load(RAW, "cell")


def classify(seconds):
    client = Client(os.path.join(DATA, "main_clf_client_raw.jsonl"), LEDGER, cap_usd=USAGE_CAP)
    rows = final_rows()
    have = load(CLF, "id")
    rng = random.Random(int(MATERIALS_HASH[8:16], 16))
    jobs = []
    for cell, r in sorted(rows.items()):
        if not r["parsed"]:
            continue
        ans = C.final_answer(r["text"])
        jobs.append((cell + "|A", C.CLASSIFIER_A, queries[r["q"]], ans))
        if rng.random() < 0.25:
            jobs.append((cell + "|B", C.CLASSIFIER_B, queries[r["q"]], ans))
    jobs = [j for j in jobs if j[0] not in have]
    print("classify todo", len(jobs), flush=True)

    def one(j):
        jid, model, q, ans = j
        res = client.chat(model, [{"role": "user", "content": C.CLASSIFIER_PROMPT.format(query=q, answer=ans)}],
                          max_tokens=300, temperature=0.0, tag=f"clf|{jid}", extra=C.reasoning_extra(model),
                          provider=C.PROVIDER_PIN[model])
        lab = (C.jload(res["text"]) or {}).get("label")
        lab = lab if lab in C.LABELS else None
        rep = False
        if lab is None:  # amendment 2: one repair attempt (network error -> same prompt, invalid label -> digit prompt)
            prompt = C.CLASSIFIER_PROMPT if res["error"] else C.CLASSIFIER_PROMPT_DIGITS
            res2 = client.chat(model, [{"role": "user", "content": prompt.format(query=q, answer=ans)}], max_tokens=300,
                               temperature=0.0, tag=f"clf_repair|{jid}", extra=C.reasoning_extra(model),
                               provider=C.PROVIDER_PIN[model])
            lab = (C.jload(res2["text"]) or {}).get("label") if res["error"] else C.parse_digit_label(res2["text"])
            lab = lab if lab in C.LABELS else None
            rep = True
        return {"id": jid, "model": model, "label": lab, "repaired": rep}
    n = pool_run(one, jobs, seconds, out_path=CLF)
    print("classified", n, "spent", round(client.spent(), 3), flush=True)


def summary():
    rows = final_rows()
    clf = load(CLF, "id")
    ledger = sum(json.loads(l).get("cost_usd") or 0 for l in open(LEDGER) if l.strip())
    print("cells done", len(rows), "of", len(cells()), "| unparsed", sum(1 for r in rows.values() if not r["parsed"]),
          "| labeled A", sum(1 for k in clf if k.endswith("|A") and clf[k]["label"]), "| ledger usd", round(ledger, 3))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "retry", "classify", "summary", "plan"])
    ap.add_argument("--seconds", type=float, default=150)
    a = ap.parse_args()
    if a.cmd == "plan":
        print("models", MODELS, "queries", Q, "prompts", len(PROMPTS), "cells", len(cells()))
        print("placebo ids", PLACEBO_IDS)
    else:
        {"run": lambda: run(a.seconds), "retry": retry, "classify": lambda: classify(a.seconds), "summary": summary}[a.cmd]()
