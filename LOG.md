# Decision log (newest first)

## 2026-11-27 (pre-pilot amendment 1; materials built; no subject model called yet)
- Author set up the key (OpenRouter, in a local .env, never read or printed by me beyond a length check), changed per_run_cap_eur to 40 (commit 72e28d4, merged into the prereg branch without editing the file), made the repo public, approved the post-pilot design rule and my generating the extra queries and paraphrases. Hard ceiling stays 40 EUR including fees.
- Checked live prices: OpenRouter model list snapshot (sha256 7394d307...) and Anthropic's pricing page. Finding: Claude Haiku 5.5 costs 0.10 / 0.50 USD per million tokens, so "Claude models are out of budget" in v1.1 was outdated. Candidates chosen by a recorded rule (8 models; N=8 instead of 6 is my disclosed choice so Anthropic's model is included).
- Built materials with helper models: 80 queries, paraphrase pools (20 lexical, 20 structural, 18 register, 10 compressed), 40 placebo variants. Cohere helper failed (reasoning leaked into text); logged and replaced by the next in the ranking. Spend so far about 0.4 USD (billed cost field), not yet in budget/ledger.csv.
- Written: studies/alignment-faking-prompt-wording/amendment-1.md (candidates, roles, pins, classifier rubric, regex, design grid and rule, money). Provider usage policies are only partly checked (OpenRouter terms via secondary summaries); stated in the amendment as an open item for the author.
- Next: runner and design-rule code, then the 960-call pilot (about 1 to 3 USD). Never edited budget/config.json; never ran approve.

## 2026-11-26 (pre-registration written, nothing run)
- At the author's request, designed a study "How robust is alignment faking to prompt wording?" (studies/alignment-faking-prompt-wording/preregistration.md, sha256 e3c6c97eb28270f9e7d88a4cb33b17b0226b2d1cb64f00d662ada3ccc9892473). Two independent review sessions found 24 and 11 problems; the file is the revised version after both. Nothing has been run and no money spent. The document itself states the honest expectation: mostly estimates with wide intervals, not a confirmed or refuted effect.
- Deviation to resolve: this study does not fit the airesearch spec schema (claims need a published value plus tolerance; this study's verdicts are interval rules), so it sits under studies/ for now. The author decides whether to extend the pipeline or accept a separate path. No spec has been frozen with `airesearch freeze`.
- Budget: expected usage about 13 USD (about 11.3 EUR) at 16 queries, about 11 USD (about 9.6 EUR) at 12 queries. The provisional per_run_cap_eur=10 would block the 16-query case; only the author can change it. The author bought 15 USD of OpenRouter credits; spend is not in budget/ledger.csv yet and is recorded when it occurs.
- This commit is on a branch so the timestamp exists before any pilot call. The author decides whether to merge it.

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
