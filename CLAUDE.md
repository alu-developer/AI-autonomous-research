# Instructions for Claude sessions

Goal: build a framework for an AI-autonomous researcher (see README.md).

Before doing anything, read in this order:
1. `docs/framework-research.md` (detailed research notes, architecture, build order, open questions)
2. `docs/blueprint.md` (short summary)
3. `LOG.md` (decisions so far)

Rules:
- Evaluator first: no generator code without a verifier in `evals/`.
- Log every decision in `LOG.md` and every run in `runs/<id>/`.
- Never claim a result without raw outputs and a human review.
- Verify details from `framework-research.md` in the primary sources before relying on them.
