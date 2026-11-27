"""Amendment 4: re-label cells whose answer changes under final_answer_last. Usage: python harness/reclassify_v2.py pilot|main"""
import gzip, json, os, random, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from or_client import Client
import common as C
HERE = os.path.dirname(os.path.abspath(__file__)); DATA = os.path.join(HERE, "..", "data"); MAT = os.path.join(HERE, "..", "materials")
which = sys.argv[1]
queries = json.load(open(os.path.join(MAT, "queries.json"), encoding="utf-8"))
rawp = os.path.join(DATA, f"{which}_raw.jsonl")
opener = (lambda p: gzip.open(p + ".gz", "rt")) if (not os.path.exists(rawp) and os.path.exists(rawp + ".gz")) else (lambda p: open(p, encoding="utf-8"))
raw = {}
for l in opener(rawp):
    if l.strip():
        r = json.loads(l)
        if r["cell"] not in raw or r["attempt"] > raw[r["cell"]]["attempt"]:
            raw[r["cell"]] = r
out_path = os.path.join(DATA, f"{which}_clf_v2.jsonl")
have = {}
if os.path.exists(out_path):
    for l in open(out_path):
        if l.strip():
            have[json.loads(l)["id"]] = json.loads(l)
client = Client(os.path.join(DATA, f"{which}_clf_v2_client_raw.jsonl"), os.path.join(DATA, "ledger.jsonl"), cap_usd=42.0)
rng = random.Random(4)
jobs = []
for cell, r in sorted(raw.items()):
    if not r["parsed"]:
        continue
    a1, a2 = C.final_answer(r["text"]), C.final_answer_last(r["text"])
    if a1 == a2:
        continue
    jobs.append((cell + "|A", C.CLASSIFIER_A, r["q"], a2))
    if rng.random() < 0.25:
        jobs.append((cell + "|B", C.CLASSIFIER_B, r["q"], a2))
jobs = [j for j in jobs if j[0] not in have]
print("changed-answer jobs", len(jobs), flush=True)

def one(j):
    jid, model, q, ans = j
    def ask(prompt, tag):
        return client.chat(model, [{"role": "user", "content": prompt.format(query=queries[q], answer=ans)}], max_tokens=300,
                           temperature=0.0, tag=tag, extra=C.reasoning_extra(model), provider=C.PROVIDER_PIN[model])
    res = ask(C.CLASSIFIER_PROMPT, f"clf_v2|{jid}")
    lab = (C.jload(res["text"]) or {}).get("label"); lab = lab if lab in C.LABELS else None
    if lab is None:
        res2 = ask(C.CLASSIFIER_PROMPT if res["error"] else C.CLASSIFIER_PROMPT_DIGITS, f"clf_v2_repair|{jid}")
        lab = (C.jload(res2["text"]) or {}).get("label") if res["error"] else C.parse_digit_label(res2["text"])
        lab = lab if lab in C.LABELS else None
    return {"id": jid, "model": model, "label": lab}
with ThreadPoolExecutor(int(os.environ.get("WORKERS", "40"))) as ex, open(out_path, "a") as f:
    for r in ex.map(one, jobs):
        f.write(json.dumps(r) + "\n"); f.flush()
print("done; spent", round(client.spent(), 3))
