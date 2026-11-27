"""Minimal OpenRouter client for the alignment-faking wording study.

Design rules (see preregistration.md):
- The API key is read from the repo's .env file and is never printed or logged.
- Every call is appended to a raw JSONL log (request hash, model, serving provider,
  billed cost from the API's own usage field, full response text).
- A spend guard aborts before a call if the cumulative billed cost in the
  ledger file would exceed the cap.
- Provider routing: fallbacks off, data collection denied.
Only the standard library is used.
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

API = "https://openrouter.ai/api/v1/chat/completions"


class SpendCapReached(RuntimeError):
    pass


def load_key(env_path=None):
    env_path = env_path or os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("OPENROUTER_API_KEY not found in .env")


def _ledger_total(ledger_path):
    if not os.path.exists(ledger_path):
        return 0.0
    tot = 0.0
    with open(ledger_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                tot += json.loads(line).get("cost_usd", 0.0) or 0.0
    return tot


class Client:
    def __init__(self, raw_log, ledger, cap_usd, key=None, extra_body=None):
        self.key = key or load_key()
        self.raw_log = raw_log
        self.ledger = ledger
        self.cap_usd = cap_usd
        self.extra_body = extra_body or {}

    def spent(self):
        return _ledger_total(self.ledger)

    def chat(self, model, messages, max_tokens=1500, temperature=1.0, tag="", extra=None,
             retries=2, provider=None):
        if self.spent() >= self.cap_usd:
            raise SpendCapReached(f"ledger total {self.spent():.4f} >= cap {self.cap_usd}")
        body = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "usage": {"include": True},
            "provider": {"allow_fallbacks": False, "data_collection": "deny"},
        }
        if provider:
            body["provider"]["order"] = [provider]
        body.update(self.extra_body)
        if extra:
            body.update(extra)
        payload = json.dumps(body).encode()
        req_hash = hashlib.sha256(payload).hexdigest()
        last_err = None
        for attempt in range(retries + 1):
            req = urllib.request.Request(
                API, data=payload,
                headers={"Authorization": "Bearer " + self.key, "Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    resp = json.load(r)
                break
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", "replace")[:500]
                last_err = f"HTTP {e.code}: {err_body}"
                if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                    time.sleep(2 ** attempt * 3)
                    continue
                resp = {"error": last_err}
                break
            except Exception as e:  # network error
                last_err = f"{type(e).__name__}: {e}"
                if attempt < retries:
                    time.sleep(2 ** attempt * 3)
                    continue
                resp = {"error": last_err}
                break
        usage = resp.get("usage", {}) or {}
        cost = usage.get("cost")
        choice = (resp.get("choices") or [{}])[0]
        text = (choice.get("message") or {}).get("content")
        rec = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "tag": tag,
            "model": model,
            "req_hash": req_hash,
            "provider": resp.get("provider"),
            "finish_reason": choice.get("finish_reason"),
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
            "cost_usd": cost,
            "error": resp.get("error"),
            "text": text,
        }
        with open(self.raw_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        with open(self.ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": rec["ts"], "tag": tag, "model": model,
                                "cost_usd": cost or 0.0}) + "\n")
        return rec
