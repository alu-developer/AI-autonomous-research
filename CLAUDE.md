# Instructions for Claude sessions

Goal: build a framework for an AI-autonomous researcher (see README.md).

Before doing anything, read in this order:
0. `docs/author-notes.md` (author's goals and constraints; never edit)
1. `docs/framework-evaluation.md` (current decision: reuse, do not build a framework)
2. `docs/framework-research.md` (detailed research notes, architecture, build order, open questions)
3. `docs/blueprint.md` (short summary)
4. `LOG.md` (decisions so far)

Rules:
- Evaluator first: no generator code without a verifier in `evals/`.
- Log every decision in `LOG.md` and every run in `runs/<id>/`.
- Never claim a result without raw outputs and a human review.
- Verify details from `framework-research.md` in the primary sources before relying on them.
