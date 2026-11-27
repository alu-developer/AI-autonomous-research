# Decision log (newest first)

## 2026-11-27 (evening: next study chosen, protocol v2)
- Author chose the next study: reproduction audits of the studies GiveWell's top-charity CEAs rely on. Budget 0 EUR. Author will not review results ("unqualified, no point"); CLAUDE.md rule changed accordingly: no human gate, results labeled machine-checked, claims kept mechanical.
- Wrote docs/audit-protocol-v2.md before opening any candidate study. New vs pilot 1: selection pool tied to GiveWell's CEAs; claims = the numbers GiveWell uses; published values confirmed by script in the PDF text layer; rerun values written by code; code edits diffed and estimation-line edits flagged (airesearch/checks.py, 6 new tests); Stata-only packages reported as a separate tier B (ported = reanalysis).
- Reasons recorded in the protocol: METR Q4 2026 update (models match skilled humans on checkable tasks, weaker judgment, model judges overrate model work, reward hacking by frontier agents).

## 2026-11-27 (late: self-review, extraction defect, study finished)
- Author said he will not review the results himself and asked to finish everything. I did an AI self-check (studies/alignment-faking-prompt-wording/review.md); it is NOT a human review and `approve` was not run, so results stay labeled machine-computed / AI-checked.
- Found my own bug: first-`<OUTPUT>` extraction read Qwen reasoning in about 17% of its replies. Wrote amendment-4 (fix rule) before any corrected number, re-labeled 768 main + 47 pilot cells (extra ~0.14 USD usage), reported both versions. No verdict changed; pilot model choice unchanged.
- Added study README, review.md, corrected results; pointer in top README. Budget cash unchanged (credits already bought).

## 2026-11-27 (main run finished; results drafted, unreviewed)
- Main run G3 finished on the author's machine: 7,200 calls, 20 unparseable after the registered retry, all labeled by classifier A (classifier B kappa 0.97 on 1,832 outputs). Two connection drops of the author's computer interrupted it; the runner resumed without gaps. Usage total 24.30 USD (3.6 pilot and materials, rest main run), recorded in budget/ledger.csv (21.13 EUR; one entry corrected after an arithmetic slip of mine). The extra credit fees (about 1.65 USD) are outside usage. Cash outlay about 27.5 EUR, under the 40 EUR ceiling.
- Registered verdicts (draft in studies/alignment-faking-prompt-wording/results.md): H1 inconclusive for both models (D = 0.037 [-0.046, 0.120] Gemini; -0.055 [-0.191, 0.081] Qwen); H3 supported for both (placebo gap about 0). The gap did not shrink under rewording but a moderate loss is not ruled out. H2 exploratory tau-hat 0.095 and 0.145. Nothing is a finding until the author reviews it; I have not run approve.
- Not done: scratchpad classifier (secondary, descriptive). Main-run raw data are in data/main_raw.jsonl.gz.

## 2026-11-27 (author chose G3; analysis and runner code committed before the main run)
- Author chose design G3 (40 queries, 23 paraphrases, 4 anchor reps; 7,200 calls) over the rule's G1 pick (amendment 3). Needs about 21 USD of usage; OpenRouter shows 15.00 bought and 3.71 used, so the author tops up about 12 USD before the run. Ceiling 40 EUR unchanged.
- Committed before any main-run call: harness/main_run.py (runner, classification with repair), harness/analysis.py (g0, mu, D, H1, H3, H2 exploratory; bootstrap B=10,000, seed 20261127, 97.5%, margin 0.05), harness/check_pipeline.py. Pipeline checks (200 simulated no-fragility studies per model, B=1,000): false "supported" H1 0.5% (Gemini) and 1.0% (Qwen), H3 0%; label-permuted pilot data: interval excludes 0 in 3.3% and 5.7% of 300 permutations (within noise of 5%; the pilot has only 12 queries). Results in results_pipeline_check.json.
- The analysis `__main__` path has not been exercised on real main data; any bug fix after the run will be a separate dated commit.

## 2026-11-27 (pilot done; models chosen; design pick pending author)
- Pilot (960 calls + 143 retries, anchor prompt only, 8 candidates) ran on the author's machine; the key never left it. Classifier A returned invalid labels for answers that comply (e.g. "dismes"), so amendment 2 added a one-time repair step (committed before the gaps were used; I had already seen the unrepaired gaps, disclosed there).
- Pilot gaps after repair (60 free / 60 paid calls each, so wide uncertainty): Gemini 3.1 Flash-Lite 0.90, Qwen 3.8 27B 0.50, Mistral Small 0.40, Meta Muse Glimmer 0.18, GPT-5.4 nano 0.05 (many missing outputs), GLM 5.3 / DeepSeek / Claude Haiku 5.5 0.00. Classifier B agrees with A on 99.1% (kappa 0.97, n=221). By the registered rule the chosen models are google/gemini-3.1-flash-lite and qwen/qwen3.8-27b. Haiku 5.5 showed no compliance, so no gap can be measured there.
- Design rule (harness/design_rule.py) picks G1 (12 queries, 23 paraphrases): about 9.7 USD projected total, simulated power 1.00 (Gemini) and 0.82 (Qwen) if rewording removes 60% of the pilot gap. Side calculation, information only: if the true gaps are half the pilot's (winner's curse), power at G1 falls to 0.85 and 0.49; G3 (40 queries, about 24 USD total) keeps 1.00 and 0.92. The author decides whether to keep G1 or sign a larger design before the main run.
- Spend: 3.59 USD billed by the API so far (3.12 EUR, recorded in budget/ledger.csv). Credit fee for the 15 USD purchase (0.83 USD) is outside usage. Never edited budget/config.json; never ran approve.

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
