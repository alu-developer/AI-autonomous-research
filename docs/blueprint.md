# Blueprint: how to build an AI-autonomous researcher

Distilled from research up to November 2026 (see `sources.md`).

## What works in existing systems
- **AI Scientist (v1/v2, Sakana/UBC/Oxford, Nature 2026):** full pipeline from idea to paper and self-review. v2 uses agentic tree search with an experiment-manager agent. Limited to computer science so far; weak at novel, high-impact hypotheses.
- **Google Co-Scientist (Nature 2026):** multi-agent hypothesis generation (generation, reflection, ranking, evolution, proximity, meta-review) with self-play debate and ranking tournaments. Validated with expert-in-the-loop lab work.
- **AlphaEvolve (DeepMind):** LLM-driven evolutionary code search with automated evaluators. Strong where results are objectively checkable (math, algorithms).

## Design lessons
1. A reliable verifier decides what works. Build the evaluator before the generator.
2. Search beats a linear pipeline: tree search, evolution, tournaments.
3. Specialized roles plus a supervisor agent.
4. Persistent shared state (files in a versioned repo).
5. Keep a human in the loop where verification is hard.

## Known failure modes (and countermeasures)
| Failure mode | Countermeasure |
|---|---|
| Falls back to outdated libraries/datasets from training data | Pin versions and datasets in the plan; check against the plan |
| Implementation drift under timeouts | Separate code generation from execution; diff implementation against spec |
| Loses context on long tasks | Shared state files, decision log, short re-grounding at each stage |
| Overstates success | Independent critic reads raw outputs, not summaries |
| Lacks tacit domain expertise | Human review of baselines and validity checks |
| Weak experimental design (single seed, infeasible compute) | Design checklist: seeds, baselines, compute budget |
| Benchmark cherry-picking, leakage, metric misuse, post-hoc selection | Preregister benchmark and metrics; report all runs; trace logs |

## Blueprint
1. Start in a domain with an automatic verifier (math, algorithms, reproducible computation).
2. Agent roles: ideator, critic, experimenter, ranker, supervisor.
3. Tree search or evolution over candidates.
4. Everything versioned in git with full logs.
5. Anti-p-hacking safeguards: preregistered metrics, fixed benchmarks, all runs reported.
6. Independent critics on raw outputs; human gate before claiming results.
7. Validate on replication tasks before open-ended discovery.

## Roadmap
- Phase 0: blueprint (this document)
- Phase 1: choose a first domain and build its verifier in `evals/`
- Phase 2: minimal loop (ideator, experimenter, critic) on one problem class
- Phase 3: add search (tree/evolution) and the ranker
- Phase 4: replication benchmark runs; then open-ended problems
