"""Independent verifier. Computes a verdict ONLY from the frozen spec and the raw results file.

Counters: overstated success (the agent's own summary is never read), implementation drift.
The agent writes numbers to outputs/results.json as {claim_id: value}; this module compares them
with the published values using the tolerance fixed in the spec before the run.
"""
from pathlib import Path

from . import runlog, spec as specmod
from .util import now_iso, read_json, sha256_file, write_json


class VerifyError(Exception):
    pass


def _within(published: float, value: float, claim: dict) -> bool:
    diff = abs(value - published)
    if "tolerance_abs" in claim and diff <= claim["tolerance_abs"]:
        return True
    if "tolerance_rel" in claim:
        denom = abs(published) if published != 0 else 1.0
        if diff / denom <= claim["tolerance_rel"]:
            return True
    return False


def verify(run_dir: Path) -> dict:
    run_dir = Path(run_dir)
    spec = specmod.load_frozen(run_dir)
    runlog.verify_chain(run_dir)
    results_path = run_dir / "outputs" / "results.json"
    if not results_path.exists():
        raise VerifyError("outputs/results.json not found; nothing to verify")
    results = read_json(results_path)

    claims_out = []
    for c in spec["claims"]:
        cid = c["id"]
        if cid not in results:
            status, value, diff = "missing", None, None
        else:
            value = results[cid]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                status, diff = "invalid", None
            else:
                diff = value - c["published"]
                status = "reproduced" if _within(c["published"], value, c) else "discrepancy"
        claims_out.append({"id": cid, "published": c["published"], "reproduced": value, "difference": diff, "status": status})

    extra = sorted(set(results) - {c["id"] for c in spec["claims"]})
    counts = {}
    for c in claims_out:
        counts[c["status"]] = counts.get(c["status"], 0) + 1
    verdict = {
        "run": spec["id"],
        "verified_at": now_iso(),
        "results_sha256": sha256_file(results_path),
        "spec_sha256": specmod.spec_hash(spec),
        "claims": claims_out,
        "counts": counts,
        "unregistered_results": extra,  # numbers reported that were not preregistered: do not treat as findings
        "all_reproduced": all(c["status"] == "reproduced" for c in claims_out),
    }
    write_json(run_dir / "verdict.json", verdict)
    runlog.append(run_dir, "verify", "verdict computed", {"counts": counts, "results_sha256": verdict["results_sha256"]})
    return verdict
