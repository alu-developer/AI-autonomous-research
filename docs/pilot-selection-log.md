# Pilot 1 selection log (2026-11-20)

Pool: first 200 Harvard Dataverse results for the preregistered query (see `pilot-protocol.md`). Mechanically eligible (R/Python/Rmd/ipynb file present, under 100 MB): 40. Order: `random.Random(20261120).shuffle(sorted DOI list)`. The checks below apply the remaining protocol conditions in that order. Decisions are rule-based; "eligible" is not a judgment of study quality.

| # | Dataset | Decision | Reason |
|---|---|---|---|
| 1 | doi:10.7910/DVN/PICQX0 (Comment on Takeishi & He, HTE test) | skipped (tentative) | no accessible paper text with numeric table found in one search; may be rechecked |
| 2 | doi:10.7910/DVN/J4HJLR (policy learning from neighbours, 3 countries) | eligible | R code, CSV data, paper text open on author site |
| 3 | doi:10.7910/DVN/KEMPRE (son preference, mental health, India) | ineligible | main tables need Stata (.do files) |
| 4 | doi:10.7910/DVN/QPAW2H (soil nutrient stress, Maharashtra) | eligible | R code, data; open preprint (Research Square) |
| 5 | doi:10.7910/DVN/FEF0QF (US economic coercion) | ineligible | accepted manuscript not openly accessible; results are figures |
| 6 | doi:10.7910/DVN/AR3MTE (acquaintance networks) | pending | paper text not yet checked |
| 7 | doi:10.7910/DVN/5QGLIG (carbon and UPP taxes, Brazil) | ineligible | the working paper with the numeric tables was not found |
| 8 | doi:10.7910/DVN/WI07KZ (Safety Tether, China NGOs) | pending | journal version access not yet checked |

Note: this pilot tests the framework; several candidates are far from the project's impact topics. That is deliberate (the author approved random selection) and is not a statement about their importance.
