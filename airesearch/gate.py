"""Human gate. Nothing is reported as a finding until a named human has reviewed the verdict.

Counters: overexcitement and unverified claims. Agents must never call approve(); the CLI requires a
reviewer name and CLAUDE.md forbids sessions from approving on the author's behalf.
"""
from pathlib import Path

from . import runlog
from .util import now_iso, read_json, sha256_file, write_json


class GateError(Exception):
    pass


def approve(run_dir: Path, reviewer: str, decision: str, note: str = "") -> dict:
    run_dir = Path(run_dir)
    if decision not in ("accept", "reject"):
        raise GateError("decision must be 'accept' or 'reject'")
    if not reviewer.strip():
        raise GateError("reviewer name required")
    verdict_path = run_dir / "verdict.json"
    if not verdict_path.exists():
        raise GateError("no verdict.json; run verify first")
    runlog.verify_chain(run_dir)
    review = {
        "reviewer": reviewer.strip(),
        "decision": decision,
        "note": note,
        "reviewed_at": now_iso(),
        "verdict_sha256": sha256_file(verdict_path),
    }
    write_json(run_dir / "review.json", review)
    runlog.append(run_dir, "review", f"{decision} by {reviewer.strip()}", {"verdict_sha256": review["verdict_sha256"]})
    return review


def report(run_dir: Path) -> str:
    """Plain-language report. Only available after human review; lists ALL claims, failures included."""
    run_dir = Path(run_dir)
    review_path = run_dir / "review.json"
    verdict_path = run_dir / "verdict.json"
    if not review_path.exists():
        raise GateError("no human review yet; a report cannot be produced")
    review = read_json(review_path)
    verdict = read_json(verdict_path)
    if review["verdict_sha256"] != sha256_file(verdict_path):
        raise GateError("verdict changed after the human review; review again")
    if review["decision"] != "accept":
        raise GateError("human review rejected this run; do not report it as a finding")
    lines = [f"# Reproduction report: {verdict['run']}", "",
             f"Reviewed by {review['reviewer']} on {review['reviewed_at']}.", ""]
    if review["note"]:
        lines += [f"Reviewer note: {review['note']}", ""]
    lines += ["| claim | published | reproduced | difference | status |", "|---|---|---|---|---|"]
    for c in verdict["claims"]:
        lines.append(f"| {c['id']} | {c['published']} | {c['reproduced']} | {c['difference']} | {c['status']} |")
    if verdict["unregistered_results"]:
        lines += ["", "Unregistered numbers (not preregistered, not findings): " + ", ".join(verdict["unregistered_results"])]
    lines += ["", f"Counts: {verdict['counts']}. Full log: log.jsonl (hash-chained)."]
    return "\n".join(lines) + "\n"
