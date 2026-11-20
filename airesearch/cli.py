"""Command line: python -m airesearch <command>.

Typical flow for one reproduction run:
  new-run <id>   -> edit runs/<id>/spec.json (claims, published values, tolerances)
  freeze <id>    -> lock the spec (no post-hoc changes)
  log <id> ...   -> record every attempt and failure
  (agent writes runs/<id>/outputs/results.json = {claim_id: number})
  verify <id>    -> independent verdict from raw results only
  approve <id>   -> HUMAN review (reviewer name required)
  report <id>    -> report, only after human acceptance
"""
import argparse
import json
import sys
from pathlib import Path

from . import budget, gate, runlog, select, spec, verify
from .util import now_iso, write_json

ROOT = Path(__file__).resolve().parent.parent


def _run_dir(root: Path, run_id: str) -> Path:
    return root / "runs" / run_id


def cmd_new_run(a, root):
    d = _run_dir(root, a.run_id)
    if d.exists():
        sys.exit(f"run {a.run_id} already exists")
    (d / "outputs").mkdir(parents=True)
    template = {
        "id": a.run_id,
        "target": {"paper": "", "doi": "", "package_url": "", "selection": "how this study was chosen (not by the agent)"},
        "pinned": {"software": {}, "data_sha256": {}},
        "claims": [{"id": "claim1", "description": "e.g. Table 2, column 3, coefficient on X", "published": 0.0, "tolerance_abs": 0.0}],
        "created": now_iso(),
    }
    write_json(d / "spec.json", template)
    runlog.append(d, "plan", "run created", {"id": a.run_id})
    print(f"created {d}/spec.json - fill it in, then run: freeze {a.run_id}")


def cmd_freeze(a, root):
    d = _run_dir(root, a.run_id)
    h = spec.freeze(d)
    runlog.append(d, "plan", "spec frozen", {"sha256": h})
    print(f"frozen {h}")


def cmd_log(a, root):
    d = _run_dir(root, a.run_id)
    e = runlog.append(d, a.kind, a.message)
    print(f"logged #{e['n']}")


def cmd_verify(a, root):
    v = verify.verify(_run_dir(root, a.run_id))
    print(json.dumps(v["counts"]), "all_reproduced=" + str(v["all_reproduced"]))


def cmd_approve(a, root):
    r = gate.approve(_run_dir(root, a.run_id), a.reviewer, a.decision, a.note or "")
    print(f"{r['decision']} by {r['reviewer']}")


def cmd_report(a, root):
    print(gate.report(_run_dir(root, a.run_id)))


def cmd_spend(a, root):
    s = budget.spend(root, a.run_id, a.amount, a.note)
    d = _run_dir(root, a.run_id)
    if d.exists():
        runlog.append(d, "spend", a.note, {"amount_eur": a.amount})
    print(s)


def cmd_budget(a, root):
    print(json.dumps(budget.status(root), indent=2))


def cmd_rank(a, root):
    path = Path(a.file) if a.file else root / "topics" / "candidates.json"
    for i, s in enumerate(select.rank(path), 1):
        flags = (" [" + ", ".join(s["flags"]) + "]") if s["flags"] else ""
        print(f"{i}. {s['score']:.2f}  {s['title']}{flags}")


def cmd_check(a, root):
    d = _run_dir(root, a.run_id)
    n = runlog.verify_chain(d)
    spec.load_frozen(d)
    print(f"ok: log chain intact ({n} entries), spec matches lock")


def main(argv=None, root: Path = ROOT):
    p = argparse.ArgumentParser(prog="airesearch")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("new-run", cmd_new_run), ("freeze", cmd_freeze), ("verify", cmd_verify), ("report", cmd_report), ("check", cmd_check)):
        sp = sub.add_parser(name)
        sp.add_argument("run_id")
        sp.set_defaults(fn=fn)
    sp = sub.add_parser("log")
    sp.add_argument("run_id")
    sp.add_argument("kind", choices=["attempt", "failure", "result", "note"])
    sp.add_argument("message")
    sp.set_defaults(fn=cmd_log)
    sp = sub.add_parser("approve")
    sp.add_argument("run_id")
    sp.add_argument("--reviewer", required=True)
    sp.add_argument("--decision", choices=["accept", "reject"], required=True)
    sp.add_argument("--note")
    sp.set_defaults(fn=cmd_approve)
    sp = sub.add_parser("spend")
    sp.add_argument("run_id")
    sp.add_argument("amount", type=float)
    sp.add_argument("note")
    sp.set_defaults(fn=cmd_spend)
    sp = sub.add_parser("budget")
    sp.set_defaults(fn=cmd_budget)
    sp = sub.add_parser("rank")
    sp.add_argument("--file")
    sp.set_defaults(fn=cmd_rank)
    a = p.parse_args(argv)
    a.fn(a, root)


if __name__ == "__main__":
    main()
