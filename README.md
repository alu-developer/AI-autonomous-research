# AI-autonomous-research

A framework for building and using an AI-autonomous researcher: a system that generates hypotheses, runs experiments, verifies results and documents everything, to produce knowledge that helps humanity.

## Status
Early stage. Phase 0: design and blueprint (see `docs/blueprint.md`).

## Layout
- `docs/blueprint.md`: design principles distilled from current research
- `docs/sources.md`: papers and systems the blueprint is based on
- `docs/framework-research.md`: detailed research notes, architecture, build order (start here)
- `CLAUDE.md`: instructions for future Claude sessions
- `agents/`: agent roles (ideator, critic, experimenter, ranker, supervisor)
- `evals/`: verifiers and benchmarks (built before the generators)
- `runs/`: full logs of every research run (one folder per run)
- `LOG.md`: decision log, newest entry first

## Principles
1. Verifier first, generator second.
2. Search over many candidates, not one linear run.
3. Log everything; every claim traces back to raw outputs.
4. A human gate before anything is claimed as a result.
