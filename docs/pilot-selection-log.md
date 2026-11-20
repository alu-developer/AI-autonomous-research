# Pilot 1 selection log (2026-11-20)

Pool: first 200 Harvard Dataverse results for the preregistered query (see `pilot-protocol.md`). Mechanically eligible (R/Python/Rmd/ipynb file present, under 100 MB): 40. Order: `random.Random(20261120).shuffle(sorted DOI list)`. The checks below apply the remaining protocol conditions in that order. Decisions are rule-based; "eligible" is not a judgment of study quality.

| # | Dataset | Decision | Reason |
|---|---|---|---|
| 1 | doi:10.7910/DVN/PICQX0 (Comment on Takeishi & He, HTE test) | skipped | two searches found no accessible text of this comment (simulation study) |
| 2 | doi:10.7910/DVN/J4HJLR (policy learning from neighbours, 3 countries) | USED (study 1) | R code, CSV data, paper text open on author site |
| 3 | doi:10.7910/DVN/KEMPRE (son preference, mental health, India) | ineligible | main tables need Stata (.do files) |
| 4 | doi:10.7910/DVN/QPAW2H (soil nutrient stress, Maharashtra) | USED (study 2) | R code, data; open preprint (Research Square) |
| 5 | doi:10.7910/DVN/FEF0QF (US economic coercion) | ineligible | accepted manuscript not openly accessible; results are figures |
| 6 | doi:10.7910/DVN/AR3MTE (acquaintance networks) | USED (study 3) | files downloaded (R scripts + 3 survey datasets, 3.5 MB; script 10 produces Tables 1-7). Paper text (Network Science, doi 10.1017/nws.2026.10047) not yet read: the web fetch needed an approval that went unanswered |
| 7 | doi:10.7910/DVN/5QGLIG (carbon and UPP taxes, Brazil) | ineligible | the working paper with the numeric tables was not found |
| 8 | doi:10.7910/DVN/WI07KZ (Safety Tether, China NGOs) | skipped | its README states models.R runs 24-48 hours on ~650,000 observations. NOTE: a runtime limit is not written in pilot-protocol.md; this skip is a deviation the author should confirm |

Note: this pilot tests the framework; several candidates are far from the project's impact topics. That is deliberate (the author approved random selection) and is not a statement about their importance.

## Later candidates (rank in seeded order)

| # | Dataset | Decision | Reason |
|---|---|---|---|
| 9 | CDEZIF (Fahey, AAC pilot) | skipped | paper not found in one search |
| 10 | UZGVAI (registrar visits, voter registration RCT) | skipped | paper not found in one search |
| 11 | EIRX7D (citizenship and democratic pendulum) | skipped | no paper text found (only a talk abstract) |
| 12 | HZ3E6R (femonationalism experiment, France) | skipped | paper not found (only conference abstract) |
| 13 | K066L4 (coastal food insecurity, marine heatwaves) | skipped | paper with that title not found in one search |
| 14 | 3BKIFP (war images) | skipped | paper not found in one search |
| 15 | 0HWU0Q (women, closed doors) | skipped | paper not found in one search |
| 16 | HXQYRR (AMIS scale) | skipped | not a regression paper; Russian-language preprint, not examined further |
| 17 | 4EQ2G1 (teaching and promotion) | ineligible | Stata .do files |
| 18 | KY2VMQ (Health Affairs survey) | skipped | publisher PDF could not be fetched |
| 19 | FWICSU (working from home and distress, Japan) | USED (study 4) | open access PDF, R code |
| 20 | TBWSLQ (populist support, medical trust) | skipped | paper not found |
| 21 | AFIW2Q (politics of parenting) | skipped | paper not found |
| 22 | B5DOOB (citizens' assemblies, Lisbon) | USED (study 5) | open preprint, R code, log files |
| 7 | 5QGLIG | ineligible | working paper with numeric tables not found |
| 8 | WI07KZ | skipped | model script runs 24-48 h; author confirmed skip (2026-11-20) |

Deviation to flag: "paper not found" skips for ranks 9-15, 20, 21 rest on one or two web searches each, not an exhaustive search. A different searcher might have found papers. Pool and order are unchanged, so this affects only which studies landed in the five, not how they were run. Also: all five used studies are social-science or health survey studies from the pool, and the paper tables used for claims were chosen by the written rule (first numbers of the main results table, or Table 2/D1 where the paper has no regression table).
