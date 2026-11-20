"""Append-only, hash-chained run log. Every attempt, including failures, is recorded.

Counters: reporting only successes, losing context on long tasks (Trehan & Chopra 2026).
Each line contains the hash of the previous line, so deleting or editing history is detectable.
"""
import json
from pathlib import Path

from .util import canonical_json, now_iso, sha256_bytes

GENESIS = "0" * 64


class LogError(Exception):
    pass


def _entry_hash(entry_without_hash: dict) -> str:
    return sha256_bytes(canonical_json(entry_without_hash))


def read(run_dir: Path) -> list:
    path = Path(run_dir) / "log.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append(run_dir: Path, kind: str, message: str, data: dict | None = None) -> dict:
    """kind examples: plan, attempt, failure, result, note, spend, review."""
    run_dir = Path(run_dir)
    entries = read(run_dir)
    prev = entries[-1]["hash"] if entries else GENESIS
    entry = {"n": len(entries) + 1, "time": now_iso(), "kind": kind, "message": message, "data": data or {}, "prev": prev}
    entry["hash"] = _entry_hash(entry)
    with open(run_dir / "log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True, ensure_ascii=False) + "\n")
    return entry


def verify_chain(run_dir: Path) -> int:
    """Return number of entries if intact, raise LogError otherwise."""
    prev = GENESIS
    entries = read(run_dir)
    for i, e in enumerate(entries, 1):
        body = {k: v for k, v in e.items() if k != "hash"}
        if e.get("n") != i:
            raise LogError(f"entry {i}: sequence number {e.get('n')} (entry removed or reordered)")
        if e["prev"] != prev:
            raise LogError(f"entry {i}: broken chain")
        if _entry_hash(body) != e["hash"]:
            raise LogError(f"entry {i}: content was modified")
        prev = e["hash"]
    return len(entries)
