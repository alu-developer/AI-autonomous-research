import json
from pathlib import Path

import pytest

from airesearch import budget, cli, gate, runlog, select, spec, verify
from airesearch.util import write_json

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def root(tmp_path):
    (tmp_path / "budget").mkdir()
    write_json(tmp_path / "budget" / "config.json", {"monthly_cap_eur": 50, "per_run_cap_eur": 10})
    return tmp_path


def make_run(root, tol=0.01):
    cli.main(["new-run", "r1"], root=root)
    d = root / "runs" / "r1"
    s = json.loads((d / "spec.json").read_text())
    s["claims"] = [
        {"id": "a", "description": "A", "published": 1.0, "tolerance_abs": tol},
        {"id": "b", "description": "B", "published": 2.0, "tolerance_rel": 0.05},
    ]
    write_json(d / "spec.json", s)
    cli.main(["freeze", "r1"], root=root)
    return d


def test_full_flow_and_report(root):
    d = make_run(root)
    write_json(d / "outputs" / "results.json", {"a": 1.005, "b": 2.5})
    cli.main(["verify", "r1"], root=root)
    v = json.loads((d / "verdict.json").read_text())
    assert [c["status"] for c in v["claims"]] == ["reproduced", "discrepancy"]
    assert not v["all_reproduced"]
    with pytest.raises(gate.GateError):  # no report before human review
        gate.report(d)
    cli.main(["approve", "r1", "--reviewer", "Alice", "--decision", "accept"], root=root)
    text = gate.report(d)
    assert "discrepancy" in text and "Alice" in text  # failures are reported, not hidden


def test_spec_change_after_freeze_is_rejected(root):
    d = make_run(root)
    s = json.loads((d / "spec.json").read_text())
    s["claims"][0]["tolerance_abs"] = 0.5  # loosen tolerance after seeing results
    write_json(d / "spec.json", s)
    write_json(d / "outputs" / "results.json", {"a": 1.3, "b": 2.0})
    with pytest.raises(spec.SpecError):
        verify.verify(d)


def test_unregistered_and_missing_results(root):
    d = make_run(root)
    write_json(d / "outputs" / "results.json", {"a": 1.0, "zzz": 9.9})
    v = verify.verify(d)
    assert v["counts"] == {"reproduced": 1, "missing": 1}
    assert v["unregistered_results"] == ["zzz"]


def test_spec_requires_tolerance_before_run(root):
    cli.main(["new-run", "r2"], root=root)
    d = root / "runs" / "r2"
    s = json.loads((d / "spec.json").read_text())
    del s["claims"][0]["tolerance_abs"]
    write_json(d / "spec.json", s)
    with pytest.raises(spec.SpecError):
        spec.freeze(d)


def test_log_tamper_detected(root):
    d = make_run(root)
    cli.main(["log", "r1", "failure", "first attempt crashed"], root=root)
    assert runlog.verify_chain(d) >= 3
    lines = (d / "log.jsonl").read_text().splitlines()
    tampered = json.loads(lines[-1])
    tampered["message"] = "everything fine"
    lines[-1] = json.dumps(tampered, sort_keys=True)
    (d / "log.jsonl").write_text("\n".join(lines) + "\n")
    with pytest.raises(runlog.LogError):
        runlog.verify_chain(d)


def test_deleted_log_entry_detected(root):
    d = make_run(root)
    cli.main(["log", "r1", "failure", "crash"], root=root)
    lines = (d / "log.jsonl").read_text().splitlines()
    (d / "log.jsonl").write_text("\n".join(lines[:1] + lines[2:]) + "\n")
    with pytest.raises(runlog.LogError):
        runlog.verify_chain(d)


def test_rejected_review_blocks_report(root):
    d = make_run(root)
    write_json(d / "outputs" / "results.json", {"a": 1.0, "b": 2.0})
    verify.verify(d)
    gate.approve(d, "Bob", "reject", "suspicious")
    with pytest.raises(gate.GateError):
        gate.report(d)


def test_verdict_changed_after_review_blocks_report(root):
    d = make_run(root)
    write_json(d / "outputs" / "results.json", {"a": 1.0, "b": 2.0})
    verify.verify(d)
    gate.approve(d, "Bob", "accept")
    write_json(d / "outputs" / "results.json", {"a": 5.0, "b": 2.0})
    verify.verify(d)  # new verdict
    with pytest.raises(gate.GateError):
        gate.report(d)


def test_budget_caps(root):
    budget.spend(root, "r1", 8, "api", when="2026-11-02T00:00:00Z")
    with pytest.raises(budget.BudgetError):
        budget.spend(root, "r1", 3, "api", when="2026-11-03T00:00:00Z")  # per-run cap 10
    for i in range(2, 6):
        budget.spend(root, f"r{i}", 10, "api", when="2026-11-04T00:00:00Z")  # total 48
    with pytest.raises(budget.BudgetError):
        budget.spend(root, "r9", 5, "api", when="2026-11-05T00:00:00Z")  # monthly cap 50
    budget.spend(root, "r9", 5, "api", when="2026-12-01T00:00:00Z")  # new month is fine


def test_ranking_flags_unsourced_and_vetoes_harm():
    ranked = select.rank(ROOT / "topics" / "candidates.json")
    assert ranked[-1]["id"] == "ai-safety-by-ai" and ranked[-1]["vetoed"]
    by_id = {r["id"]: r for r in ranked}
    assert "unsourced:importance" in by_id["repro-audits"]["flags"]  # missing sources are flagged
    assert "unsourced:importance" in by_id["global-priorities"]["flags"]
    # an unsourced factor is capped, so it cannot inflate the score
    t = {"id": "x", "title": "x", "scores": {"importance": 5, "neglectedness": 5, "tractability_ai": 5, "verifiability": 5}, "sources": {}}
    assert select.score(t)["score"] < 3.5
