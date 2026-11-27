# Protocol: reproduction audits of papers The Unjournal chose to evaluate

Written 2026-11-27, before any paper in the pool was opened. Mechanics (two independent checks per number, code-change policy, tiers, labels, no human review) are those of `docs/audit-protocol-v2.md`; only the differences are listed here. Author's decisions: topic chosen (chat, 2026-11-27); budget 0 EUR; no human review.

Seen before writing: column names and value counts of the Unjournal's public `data/research.csv` (repo unjournal/unjournaldata, commit feb1c6da0e28e9f1615d26c0c7baf4ef105889cf, MIT licence). No titles, papers or packages.

## Question
For papers The Unjournal has publicly evaluated, does the authors' own public replication package reproduce the first three point estimates of the paper's main results table?

Why this pool: choosing which research matters is judgment, where AI is weaker than experts. The Unjournal makes that choice by stated criteria (importance to global priorities, relevance to decisions, influence). We only do the checkable part.

## Selection
1. **Pool:** rows of `research.csv` at the commit above with status `50_published evaluations (on PubPub, by Unjournal)`.
2. **Order:** sort by `research_url`, then shuffle with `random.Random(20261127)`. Attempt in that order; never skip by preference.
3. **Eligibility** (first failing item recorded), protocol v2 rules 3a–3d, plus:
   - 3e **terms:** the package's licence or terms must not forbid automated or AI processing (lesson from the Cochrane case). Unclear terms are recorded and the study is skipped.
   - 3f **not already reproduced:** skip if the Institute for Replication (I4R) has published a reproduction of the same paper (checked by title search of I4R discussion papers). Recorded with the link.
4. **Stop:** after 10 studies reach an outcome other than `ineligible`, or when the pool is exhausted.

## Claims
The first three point estimates (coefficients, effects or means) in the paper's first main-text results table, read row by row, in the version linked by the Unjournal. If the package ships a different paper version, the version used is recorded. Tolerance: 1% relative or 3 units of the last printed digit, whichever is larger.

## Reporting
Labels and gate as in protocol v2 ("machine-checked, not human-reviewed"). Results per study and in aggregate; aggregate numbers describe this sample only. Authors or the Unjournal are contacted only with the author's explicit OK for each message.
