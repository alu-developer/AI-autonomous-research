# Decision log (newest first)

## 2026-11-23 (exploratory toy study, outside the pipeline)
- At the author's request (curiosity, not a research run): built toy money-flow models of the stock market (studies/stock-market-flow-model/: pool model, extensions, portfolio model, cohort model, 3 experiment scripts with self-tests). Not preregistered, not human-reviewed, so NOT a finding. Real-world data points in its README come from web searches and are unverified. Open question recorded there: can credit/money creation supply unlimited inflow (the two models disagree).

## 2026-11-20 (pilot 1 done)
- Ran pilot 1 (5 studies, protocol in docs/pilot-protocol.md, results in docs/pilot-1-results.md): 11 of 15 numbers reproduced, 4 discrepancies (both from paper/code version mismatches). Cost 0 EUR. Nothing approved; results stay "machine-verified, unreviewed". Author decided: skip WI07KZ (24-48 h runtime). Open: human-gate policy, independent extraction step.

## 2026-11-20 (night)
- Built framework v0.1 (airesearch/: spec lock, hash-chained run log, independent verifier, human gate, budget caps, topic ranking) with 10 passing tests. per_run_cap_eur=10 is provisional (author to confirm). Next: pilot on topic 1.

## 2026-11-20 (evening)
- GitHub connected; repo alu-developer/AI-autonomous-research pushed (private). Wrote docs/topic-candidates.md (topics first, then frameworks, per author's request). Finding: top candidate is verification/reproduction audits (topic 1); big AI-scientist frameworks do not fit the top topics.

## 2026-11-20 (later)
- Author clarified goals (see docs/author-notes.md). Evaluated open frameworks (docs/framework-evaluation.md). Decision: reuse existing tools, build only a small 'research director' layer (problem selection, human gate, budget, audit). Earlier plan to build a full framework dropped.

## 2026-11-20
- Repo created. Decision: GitHub repo as source of truth, work in the cloud, local clone only if heavy compute or private data is needed.
- Decision: blueprint based on literature review; first domain still open.
