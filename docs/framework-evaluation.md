# Evaluation of open frameworks vs. the author's requirements (2026-11-20)

Requirements (see `author-notes.md`): the system picks high-impact problems itself; human decides topic + money only; ~50 EUR/month; no GPU; no server yet; results go to people who can act; avoid harm.

Provenance: based on search snippets and a few fetched pages. Licenses and cost figures marked "unverified" must be checked in the repo before use.

| System | What it is | Fit | Why |
|---|---|---|---|
| AI Scientist-v2 (Sakana) | End-to-end ML paper pipeline, tree search | Poor | Needs Linux + NVIDIA GPU + CUDA; domain is ML experiments; user must write a topic file (no autonomous problem choice); custom Responsible-AI-style license with AI-disclosure requirement; ~15-20 USD per run (author figure) |
| Karpathy autoresearch | 3-file loop: agent edits train.py, 5-min GPU run, keep/revert | Pattern yes, tool no | Brilliant minimal pattern (fixed evaluator, single editable file, program.md as human interface, git as tracker) but built for LLM training on a GPU |
| OpenEvolve / ShinkaEvolve / CodeEvolve | Open AlphaEvolve-style evolutionary coding | Good when a verifier exists | Cheap, CPU-friendly for math/algorithm tasks; needs a machine-checkable score. Licenses unverified. CodeEvolve (EMNLP 2026 Findings) claims to beat both under matched budgets |
| Agent Laboratory (JHU/AMD) | LLM research-assistant pipeline | Maybe as reference | Human co-pilot mode, cheap per paper in its own paper; ML-focused; maintenance status unverified |
| freephdlabor | Open multi-agent, dynamic workflow, customizable | Reference | Modular design to learn from; maturity unverified |
| OpenScientist (WashU) | Open co-scientist built on Claude Code + domain Agent Skills, Apache 2.0 | Good pattern | Same technical base as this environment; biomedical focus; scientist supplies the question |
| K-Dense scientific-agent-skills | 130-160 skills for any Agent-Skills-compatible agent (Claude Code etc.) | Good building block | Free; adds databases and workflows to a coding agent |
| OpenAGS | Open framework for literature to manuscript, SDK-agnostic | Reference | Maturity unverified |
| Kosmos (Edison) | Strongest autonomous system reported | Not usable | Closed, commercial platform; 79.4% of 102 checked statements were supported by experts, i.e. about 1 in 5 not |
| Robin (FutureHouse) | Lab-in-the-loop biomedical | Not usable | Needs wet lab; partly closed platform |
| Google Co-Scientist | Hypothesis generator | Not usable directly | Experimental access only; ideas reusable (tournament, reflection) |

## Cross-cutting finding that matters most for this project
No evaluated system chooses high-impact problems itself. A May 2026 position paper argues AI pushes research towards what is easy to measure (McNamara fallacy), and finds hypotheses from different models are strongly similar ("hypothesis hivemind"), so using several models gives less diversity than hoped. Recommendations there: persistent mutable belief state, preregistered hypotheses, diversity-preserving prompting. A Dec 2025 HybridQuestion paper (Tsinghua) uses human-AI filtering to select high-impact questions. PrimeScientist (Sep 2026) studies how to allocate research effort across directions under a budget.

## Decision
Do not build a general research framework. Reuse, and build only the missing layer:
1. **Agent core:** Claude Code or Agent SDK sessions with scientific skills (K-Dense collection, OpenScientist-style skills). No custom orchestration.
2. **Evaluator-based search:** OpenEvolve-family tools, only for problems with a machine-checkable score.
3. **New, small, custom layer ("research director"):** (a) problem-selection pipeline: candidate problems scored on importance, tractability, neglectedness, AI-doability, harm risk, with sources; (b) human gate: the author picks topic and budget; (c) budget tracker; (d) run records and audit trail; (e) independent critic on raw outputs; (f) results written for non-academic decision makers.
4. First deliverable: a ranked, sourced shortlist of candidate problems for the author to choose from.

## Open items
- Verify licenses and activity of OpenEvolve, ShinkaEvolve, K-Dense skills, OpenScientist, Agent Laboratory.
- Decide where unattended runs happen (scheduled cloud sessions vs a small VPS).
