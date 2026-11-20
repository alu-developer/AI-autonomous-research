# AI-autonomous-research

A thin "research director" layer for AI-run research that aims to help people. It does not replace existing agents or frameworks; it keeps their work honest. Goals, constraints and the author's role are in `docs/author-notes.md` (read first, never edit).

## What it enforces (and why)
| Rule | Counters (from the research notes) | Code |
|---|---|---|
| Preregistered claims and tolerances, frozen by hash | post-hoc selection, metric misuse | `airesearch/spec.py` |
| Hash-chained, append-only log of every attempt | losing context, hiding failures | `airesearch/runlog.py` |
| Verdict computed only from raw results vs frozen spec | overstated success, implementation drift | `airesearch/verify.py` |
| Human review before any report; reports list all claims | unverified claims | `airesearch/gate.py` |
| Hard monthly and per-run budget set by the author | runaway cost | `airesearch/budget.py` |
| Transparent topic ranking; unsourced scores capped; harm veto | problem-selection bias | `airesearch/select.py`, `topics/candidates.json` |

## Use
```
python -m airesearch rank                      # topic ranking (advice; the author decides)
python -m airesearch new-run <id>              # then edit runs/<id>/spec.json
python -m airesearch freeze <id>               # lock the spec before running anything
python -m airesearch log <id> failure "..."    # log every attempt and failure
# the agent writes runs/<id>/outputs/results.json = {claim_id: number}
python -m airesearch verify <id>               # independent verdict
python -m airesearch approve <id> --reviewer NAME --decision accept   # HUMAN only
python -m airesearch report <id>
python -m airesearch budget / spend <run> <eur> "<note>"
python -m pytest -q                            # tests
```

## Layout
- `airesearch/`: the package; `tests/`: tests
- `topics/candidates.json`: scored candidate topics; `budget/`: caps (author-owned) and ledger
- `runs/<id>/`: one folder per run (spec, lock, log, outputs, verdict, review)
- `agents/`: role prompts for sessions (reproducer, critic); `evals/`: reserved for domain verifiers and benchmarks
- `docs/`: `author-notes.md` (author's words), `framework-evaluation.md` (why reuse + why not the usual AI scientist), `topic-candidates.md`, `framework-research.md`, `blueprint.md`, `sources.md`
- `LOG.md`: decision log, newest first. `CLAUDE.md`: rules for Claude sessions

## Status
Framework v0.1 built and tested. Next: pilot (topic 1: reproduction audits). Nothing here has produced a research result yet.
