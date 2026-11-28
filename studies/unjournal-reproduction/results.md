# Results: reproduction audits of papers The Unjournal evaluated

**Status: machine-checked, not human-reviewed.** Protocol: `protocol.md` (with `docs/audit-protocol-v2.md`). Cost: 0 EUR. Dates: 2026-11-27 to 2026-11-28.

## Outcome
The whole pool of 58 papers with published Unjournal evaluations was checked in the seeded order (`order.json`, `eligibility-log.md`). The stop rule (10 audited papers) was not reached; the pool ran out.

| Status | Papers |
|---|---|
| Audited: authors' public code rerun | 4 |
| Eligible only as a Stata port (tier B), not run | 1 |
| Ineligible: code in Matlab | 1 |
| Ineligible: package behind a login (openICPSR), bot protection, or proprietary data | 8 |
| Ineligible: no public package found, or no data (theory, reviews, posts) | 44 |

All 4 audited papers reproduced: **12 of 12 numbers** within tolerance.

| Run | Paper | Claims | Result |
|---|---|---|---|
| uj03-ssn-women | Social safety nets and women's economic achievements and agency (meta-analysis) | Table 2, 3 meta-regression coefficients | 3/3 (e.g. 0.033 published, 0.0334 rerun) |
| uj04-popethics | Population ethical intuitions (Cognition 2022) | Table 1, 3 mean ratings | 3/3 (e.g. 5.12 vs 5.117) |
| uj08-xpt | Forecasting Existential Risks (XPT, FRI 2023) | Table 1, 3 median forecasts | 3/3 (9.05% vs 9.045%, 20% vs 20%, 1% vs 1%) |
| uj48-meat-meta | Reducing meat and animal product consumption (meta-analysis, OSF v4) | Table 1, 3 pooled SMDs | 3/3 (whole table matches) |

## What this says (narrow claims)
1. Where the authors' own R code was public, it reproduced the headline numbers in all 4 cases, after environment fixes only.
2. Only 4 of 58 papers (7%) could be checked this way from a cloud workspace with free tools and no logins. Most economics working papers have no public package, or only one behind openICPSR's login.
3. The environment problems found are reported because they will break future reruns: a deprecated dplyr function and unloaded packages (uj04); a breaking change in the `aggutils` dependency since the report (uj08: needed the 2023 version); a long sensitivity analysis that stalls a full run (uj03).

## Deviations and my own errors (all in the run logs)
- uj03: full script stalled after Table 2; rerun stopped after the Table 2 models (later code cannot change them).
- uj03: my first code diff converted line endings; redone.
- uj08: my runner was broken by the script's `rm(list = ls())`; fixed. My spec named the wrong group label for one claim (`expertG1` instead of the code's `all experts`); corrected after I had seen the printed medians, disclosed in the log.
- uj08 and uj48: tolerances tightened before running (the protocol rule would have allowed +-3 percentage points or +-0.03 SMD).

## Limits
- Which table cells to check was my reading of "first results table"; recorded per spec.
- Published numbers were read by me and confirmed by script in the PDF text layer; no second independent extractor.
- Eligibility checks were 1 to 4 searches per paper (Dataverse, Zenodo, OSF, GitHub APIs, web search). "No package found" is provisional; a package may exist elsewhere.
- A reproduced number does not mean the analysis is right: coding errors that still produce the published number are not detected.
