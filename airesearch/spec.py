"""Preregistration. A spec names the claims to reproduce and the tolerance BEFORE any run.

Counters: post-hoc selection bias, metric misuse, benchmark cherry-picking (Luo et al. 2025).
Once frozen, the spec's hash is stored in spec.lock; the verifier refuses a changed spec.
"""
from pathlib import Path

from .util import canonical_json, now_iso, read_json, sha256_bytes, write_json

REQUIRED_TOP = ("id", "target", "claims")


class SpecError(Exception):
    pass


def validate(spec: dict) -> None:
    for key in REQUIRED_TOP:
        if key not in spec:
            raise SpecError(f"spec missing '{key}'")
    if not spec["claims"]:
        raise SpecError("spec has no claims")
    seen = set()
    for c in spec["claims"]:
        for key in ("id", "description", "published"):
            if key not in c:
                raise SpecError(f"claim missing '{key}': {c}")
        if c["id"] in seen:
            raise SpecError(f"duplicate claim id {c['id']}")
        seen.add(c["id"])
        if "tolerance_abs" not in c and "tolerance_rel" not in c:
            raise SpecError(f"claim {c['id']} needs tolerance_abs or tolerance_rel (decide before running)")


def spec_hash(spec: dict) -> str:
    return sha256_bytes(canonical_json(spec))


def freeze(run_dir: Path) -> str:
    """Validate spec.json and write spec.lock. Refuses to re-freeze a different spec."""
    run_dir = Path(run_dir)
    spec = read_json(run_dir / "spec.json")
    validate(spec)
    h = spec_hash(spec)
    lock = run_dir / "spec.lock"
    if lock.exists():
        old = read_json(lock)["sha256"]
        if old != h:
            raise SpecError("spec already frozen with a different content; create a new run instead")
        return h
    write_json(lock, {"sha256": h, "frozen_at": now_iso()})
    return h


def load_frozen(run_dir: Path) -> dict:
    """Load spec and check it still matches the lock."""
    run_dir = Path(run_dir)
    lock = run_dir / "spec.lock"
    if not lock.exists():
        raise SpecError("spec is not frozen; run 'freeze' before verifying")
    spec = read_json(run_dir / "spec.json")
    validate(spec)
    if spec_hash(spec) != read_json(lock)["sha256"]:
        raise SpecError("spec.json changed after freezing (post-hoc change); the run is invalid")
    return spec
