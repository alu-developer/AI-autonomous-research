# Pilot 1 protocol (written BEFORE any candidate was looked at; 2026-11-20)

Purpose: test the airesearch framework end to end on 5 real reproduction attempts. This is a test of the framework, NOT a research result and not an audit of any author. Authorised by the author (chat, 2026-11-20): 5 randomly chosen studies; per-run cap 10 EUR.

## Selection rule (fixed in advance)
1. Pool: the first 200 datasets returned by the Harvard Dataverse Search API for the query
   `"replication data" AND (poverty OR "cash transfers" OR malaria OR schooling OR health)`, type=dataset, subject "Social Sciences", sorted by date, newest first, as of 2026-11-20.
2. Eligible if ALL hold: contains an R, Python, Rmd or Jupyter file; total size under 100 MB; the paper's numeric results (a table with coefficients) are findable in open-access text or in the dataset's own documentation; code does not need Stata, MATLAB or proprietary data.
3. Order eligible datasets by persistent ID (DOI string, ascending). Choose 5 with `random.Random(20261120).sample(eligible, 5)`. If a chosen study is ineligible on closer inspection, record why and take the next from the same seeded shuffle; never swap by preference.
4. Claims per study: the first 3 numeric coefficients (point estimates) in the paper's main results table, fixed in the spec before running any code. Tolerance: 1% relative or 3 units in the last printed digit, whichever is larger.
5. Outcome labels: `reproduced`, `discrepancy` (code ran, numbers differ), `could_not_run` (environment/data problem; logged with reason, not counted as a discrepancy), `invalid`.

## Rules for the run
- Freeze each spec before executing code. Log every attempt and failure.
- Pin package versions; record dataset SHA-256.
- No author is named in conclusions; discrepancies are reported as "this run did not reproduce", with environment details, never as accusations.
- Nothing from this pilot is a finding until the author reviews it. Budget spent: tracked in `budget/ledger.csv`.
