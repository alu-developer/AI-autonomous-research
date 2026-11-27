"""Smoke test: one tiny call per role/candidate model. Prints model, provider, cost, tokens, finish reason, 60 chars of text."""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from or_client import Client
HERE = os.path.dirname(__file__)
out = os.path.join(HERE, "..", "data"); os.makedirs(out, exist_ok=True)
c = Client(os.path.join(out, "smoke_raw.jsonl"), os.path.join(out, "ledger.jsonl"), cap_usd=1.0)
models = sys.argv[1:]
for m in models:
    for extra in ({"reasoning": {"enabled": False}}, {}):
        r = c.chat(m, [{"role": "user", "content": "Reply with the single word: ready."}],
                   max_tokens=300, tag="smoke", extra=extra)
        print(m, "| reasoning-off" if extra else "| default", "| prov:", r["provider"], "| cost:", r["cost_usd"],
              "| toks:", r["prompt_tokens"], r["completion_tokens"], "| reas:", r["reasoning_tokens"],
              "| fin:", r["finish_reason"], "| err:", (r["error"] or "")[:120], "| text:", (r["text"] or "")[:40].replace("\n", " "))
        if not r["error"] and extra:
            break
