# Results: reproduction audits of studies GiveWell relies on

**Status: machine-checked, not human-reviewed.** Protocol: `docs/audit-protocol-v2.md` plus amendments 1 and 2. Cost: 0 EUR. Date: 2026-11-27.

## Outcome
No study could be reproduced under the protocol. Of 9 studies that GiveWell names as sources of effect sizes for its four top charities and its cash benchmark (`pool.csv`):

| Status | Studies | Which |
|---|---|---|
| Excluded: Cochrane terms forbid AI processing | 3 | nets, SMC, vitamin A (the main mortality/incidence inputs) |
| No public package, or only behind a login | 5 | New Incentives RCT, Tagbor 2016, Bleakley 2010, Cutler 2010, Walker 2025 |
| Eligible only as a Stata port (tier B), not run | 1 | Egger 2022 |
| Reproduced / discrepancy | 0 | - |

## What this says (narrow claims)
1. The evidence behind GiveWell's largest grants cannot be re-run openly by an AI-run project with free tools: the three central inputs are Cochrane meta-analyses whose terms forbid AI processing without permission, and most other inputs have no public package or need a login.
2. Where packages exist, they have already been checked for GiveWell: Bleakley 2010 (Roodman 2018, pre-registered reanalysis, largely robust) and Egger 2022 (Wiebe 2024 reanalysis; authors' own code correction 2026). An outside reproduction would add little.
3. So this topic is less neglected, and less open to AI-run checking, than `docs/topic-candidates.md` assumed for "studies that drive big funding decisions".

## Limits
- Package searches were 1 to 3 searches per study; a package could exist elsewhere.
- GiveWell's CEA spreadsheets were not opened; the pool comes from GiveWell's report pages, so studies used only inside the spreadsheets may be missing.
