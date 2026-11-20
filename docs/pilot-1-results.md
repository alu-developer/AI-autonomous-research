# Pilot 1 results (2026-11-20): reproduction audits, 5 studies

Status: machine-verified, NOT human-reviewed (no `approve` was run). Protocol: `pilot-protocol.md`. Selection: `pilot-selection-log.md`. Runs: `runs/pilot*/` (frozen spec, hash-chained log, outputs, verdict). Cost: 0 EUR.

| Run | Study (Harvard Dataverse) | Claims checked | Verdict |
|---|---|---|---|
| pilot1-j4hjlr | Policy learning from neighbours (J4HJLR) | Table 2, 3 Distance coefficients | 0 of 3 reproduced (discrepancy) |
| pilot2-qpaw2h | Soil nutrient stress, Maharashtra (QPAW2H) | Table 3, 3 coefficients | 3 of 3 reproduced, after a one-line namespace fix |
| pilot3-ar3mte | Acquaintance networks (AR3MTE) | Table 2, 3 means | 3 of 3 reproduced, code unchanged |
| pilot4-fwicsu | Working from home and distress, Japan (FWICSU) | Table 5, 3 odds ratios | 2 of 3 reproduced, 1 discrepancy (2.29 vs 2.25) |
| pilot5-b5doob | Citizens' assemblies, Lisbon (B5DOOB) | Table D1, 3 coefficients | 3 of 3 reproduced, after environment fixes |

Total: 11 of 15 numbers reproduced within the preregistered tolerance (1% or 3 units of the last digit); 4 discrepancies. These counts are about this sample of five, not about the field.

## What this says about the framework
- The mechanics worked: specs frozen before running, failures logged (5 runs had at least one failure or environment fix), verdicts computed by script, no unregistered numbers reported.
- Most effort went into the environment, not the science: missing packages, a masked function (`select`), a missing `library(dplyr)`, a file-name case mismatch (works on macOS/Windows, fails on Linux), Dataverse `.tab` naming of CSV files. Each is logged as a failure or deviation.
- Both discrepancies (studies 1 and 4) came with a documented version mismatch between the paper and the shipped code (study 1: different sample sizes and an extra covariate; study 4: the paper's Table 5 has month fixed effects and education dummies that the shipped code lacks). They are version mismatches, not accusations against authors.

## Weak points to fix before relying on this
1. The extraction steps are not independent: I copied published numbers from the PDF and rerun numbers from console output myself. A copying error would pass the verifier. Needs a second extractor or a human spot check.
2. Published numbers for study 3 came through a fetch tool that summarizes page text (second-hand); they matched the rerun exactly, which makes an error unlikely but it is not proof.
3. "Paper not found" skips (ranks 9-15, 20, 21) rest on one or two searches each. See the deviation note in the selection log. Study 8 was skipped for runtime (author confirmed).
4. The rule for "first 3 numbers" had to be interpreted for papers without regression tables (studies 3 and 5). The interpretations are written in each spec.
5. All five studies are social-science/health survey papers, chosen by pool and seed, not by importance. This pilot tests the pipeline, not topic 1's value.
6. The human gate is untested: nothing was approved, and the author has not decided how strict it should be.

## Suggested next steps (for the author to decide)
- Decide the human-gate policy (who reviews, how much, what happens if nobody does).
- Add a second-extractor or spot-check step.
- Then run topic 1 on studies that matter for funding decisions, with the pipeline as is.
