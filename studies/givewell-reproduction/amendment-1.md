# Amendment 1 (2026-11-27, before any study data, table or package was opened)

**What I found while building the pool:** GiveWell's main mortality/incidence inputs for three of the four top charities come from Cochrane meta-analyses, not single studies with code:
- nets (AMF): Pryce et al. 2018, Analysis 1.2, rate ratio 0.55 (via GiveWell's ITN report);
- SMC (Malaria Consortium): Meremikwu et al. 2012, rate ratio 0.26;
- VAS (Helen Keller): Imdad et al., random-effects estimate, 24% mortality reduction.
Under protocol v2 rule 3c (code in R/Python/Stata) these would all be ineligible, so the audit would skip the numbers that matter most. I know only the headline numbers above, as quoted on GiveWell pages; I have not opened the reviews' per-trial data.

**Change:** add **tier M (meta-analyses)**. Eligible if the review publishes per-trial data for the analysis GiveWell uses (events/totals or estimates with SEs, in its "Data and analyses" section). I re-enter the per-trial data, recompute the pooled estimate in R (`metafor`) with the method the review states, and compare with the published pooled value and CI bounds (same tolerance as tier A).
- Copying check: each per-trial number is confirmed in the review's PDF text by `checks.py confirm-pdf` (unconfirmed numbers make the whole analysis `extraction_unconfirmed`).
- Recompute code is written before data entry and frozen with the spec.
- Reported separately from tier A (authors' own code) and tier B (ported Stata).
- Not checked in tier M: whether trials were selected or extracted correctly from the original trial papers.

Everything else in protocol v2 is unchanged.
