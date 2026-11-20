# Instructions for Claude sessions

Goal: research that helps people, done by AI under the author's direction (see README.md).

Before doing anything, read in this order:
0. `docs/author-notes.md` (author's goals and constraints; NEVER edit unless the author explicitly says so)
1. `docs/framework-evaluation.md` (why we reuse existing tools and why not the usual "AI scientist")
2. `README.md` (what the airesearch package enforces and how to use it)
3. `LOG.md` (decisions so far), then `docs/topic-candidates.md`
4. `docs/framework-research.md` / `docs/blueprint.md` only when needed (background)

Rules:
- The author decides topics and money. Propose, never decide. Never edit `budget/config.json`.
- Every research run goes through `python -m airesearch`: freeze the spec BEFORE running, log every attempt including failures, let `verify` compute verdicts from raw results.
- NEVER run `approve`. Only the human author does. Never claim a result without a human-reviewed report.
- Do not report numbers that were not preregistered as findings.
- Choose studies/benchmarks by a rule recorded in the spec (not by what looks promising to you).
- Pin software and data versions in the spec; record dataset hashes.
- Verify details from the research notes in primary sources before relying on them.
- Keep dual-use and harm risk in mind; if a topic conflicts with public benefit, stop and ask.
- Log every decision in `LOG.md`. Run `python -m pytest -q` before committing.
