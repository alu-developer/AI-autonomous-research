# Protocol v2: reproduction audits of studies GiveWell relies on

Written 2026-11-27, before any candidate study was opened. Supersedes `pilot-protocol.md` for this study.
Author's decisions (chat, 2026-11-27): topic chosen; budget 0 EUR; **no human review** (the author will not review results and asked that nothing wait for him). Everything below is built so that the result can be trusted without a reviewer, by keeping claims narrow and checks mechanical.

Disclosure: before writing this, I had seen the names of some studies GiveWell uses (GiveDirectly cash-transfer RCTs, the Kremer et al. water meta-analysis) in web searches. I have not opened any replication package or table for this study.

## Question
For the studies whose estimates GiveWell feeds into the cost-effectiveness analyses (CEAs) of its current top charities, does the authors' own public replication package, run unchanged, reproduce the specific numbers GiveWell uses?

This is a narrow, checkable question. It does **not** ask whether a study is right, whether GiveWell's use of it is right, or whether a program works.

## Why this design (lessons from the project so far)
| Risk | From | Countermeasure here |
|---|---|---|
| AI judgment is weaker than experts' where there is no clear check | METR Q4 2026 update | Only mechanical claims: number in paper vs number from code |
| A model checking a model overrates the work | METR Q4 2026 update | Checks are scripts, not a second model's opinion |
| Reward hacking: gaming the check instead of doing the task | METR Q4 2026 update | Tolerances, claims and check code frozen before running; code edits limited and machine-checked; verdicts only by `verify` |
| Copying errors pass the verifier (pilot weak point 1) | Pilot 1 | Published values confirmed by a script in the PDF text; rerun values written to JSON by code, never typed by me |
| Selection by what looks promising | Blueprint | Pool and order fixed by rule below |
| Environment fixes silently change the analysis | Pilot 1 | Every edit saved as a diff; edits touching estimation lines flagged automatically |

## Selection rule
1. **Charities:** GiveWell's Top Charities as listed on givewell.org on the day the pool is built (expected: AMF, Malaria Consortium SMC, Helen Keller Intl VAS, New Incentives). Plus GiveDirectly, because GiveWell uses cash transfers as its benchmark. The list as found is recorded with a page snapshot hash.
2. **Studies:** for each charity, every study that GiveWell's published CEA or intervention report names as the source of an effect size that enters the CEA (mortality, income, consumption, coverage effects). Studies cited only for background are out. Recorded in `studies/givewell-reproduction/pool.csv` with the page and passage that names each one.
3. **Eligibility** (all must hold, checked in this order; the first failing item is recorded):
   a. a public replication package exists (Dataverse, Zenodo, OSF, journal site, or openICPSR without login);
   b. the data needed for the claimed numbers are inside the package (not restricted or "on request");
   c. code is in R or Python (tier A), or Stata (tier B, see below);
   d. expected runtime under 6 hours on this workspace.
4. **Order:** eligible studies sorted by the GiveWell grant volume of the charity (largest first, as stated by GiveWell), then by DOI. All eligible studies are attempted in that order until the pool is exhausted or the time cap is hit. Nothing is skipped by preference.

## Claims per study
- The number(s) GiveWell takes from the study (up to 3), each tied to a specific table cell in the paper. If GiveWell's number is a transformation (for example a pooled or adjusted value), the claim is the paper's untransformed cell, and the link is written in the spec.
- If GiveWell names the study but no specific number, the first 3 point estimates of the paper's main results table (as in pilot 1).
- Tolerance: 1% relative or 3 units in the last printed digit, whichever is larger. Fixed in the spec before running.

## Two independent checks per number
1. **Published value:** I read it from the paper, then `airesearch/checks.py confirm-pdf` must find that exact printed string in the PDF's text layer on the stated page. If it cannot (scanned PDF, layout split), the claim is marked `extraction_unconfirmed`: reported, but not counted.
2. **Rerun value:** written to `outputs/results.json` by code added at the end of the authors' script (for example `jsonlite::write_json(coef(m)[...])`). I never type a rerun number.

## Code-change policy
- Allowed: install packages, set paths, fix file-name case, convert `.tab` back to the original format, add missing `library()` calls, append the results-writing lines.
- Every change is saved as `outputs/code.diff`. `checks.py check-diff` flags any changed line containing an estimation or sample command (R: `lm`, `glm`, `feols`, `felm`, `lmer`, `subset`, `filter`; Stata: `reg`, `areg`, `xtreg`, `ivreg`, `keep`, `drop`, `if`). A flagged change makes the run's claims count as `modified`, not `reproduced`.

## Tier B: Stata-only packages
Stata is not free. Tier B packages are ported to R by me. That is a reanalysis, not a reproduction, and porting can introduce errors. Tier B results are reported separately and never mixed into tier A counts. The number of tier B and ineligible studies is itself reported: it says how much of the evidence behind these grants cannot be rerun with free software.

## Outcome labels
`reproduced`, `discrepancy` (code ran, number outside tolerance), `modified` (flagged code change), `extraction_unconfirmed`, `could_not_run` (environment or data problem, reason logged), `ineligible` (with the failing rule).

## Gate and reporting
- No human review. Reports are labeled **"machine-checked, not human-reviewed"**. `approve` is not run.
- Every study in the pool appears in the report with its status, including ineligible ones.
- Discrepancies are stated as "this run of the authors' package did not reproduce cell X (published a, rerun b)", with environment details. Never as an accusation or as a claim that a study or a GiveWell estimate is wrong.
- Authors or GiveWell are contacted only with the author's explicit OK for each message.

## Limits fixed in advance
- Money: 0 EUR (no API calls, no paid software).
- Time: stop after 15 attempted studies or when the pool is exhausted; report whatever is done.
- Not checked: whether the right number was chosen by GiveWell, coding errors that still reproduce the published number, robustness to other specifications.
