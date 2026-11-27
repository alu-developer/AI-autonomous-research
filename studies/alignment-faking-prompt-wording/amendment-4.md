# Amendment 4 (2026-11-27, after the main run): answer-extraction defect found in my own review

**What I found.** While spot-checking labeled answers I saw Qwen "answers" that were reasoning text. The cause is in my code, not in the registered rule: `final_answer()` in `harness/common.py` takes the text after the **first** `<OUTPUT>` it sees. When Qwen's private reasoning quotes the tag (for example "only the text inside <OUTPUT> tags is shown"), the first occurrence is inside the reasoning, so classifier A saw reasoning, not the answer. The registered rule says the final answer is the text of the answer block, which is the last `<OUTPUT>` in the reply. Counts in the main run: Gemini always has exactly one `<OUTPUT>` (no problem); Qwen has two or more `<OUTPUT>` strings in about 17% of its parsed outputs (about 570 of 3,600 calls). The same code produced the pilot labels, so the pilot gaps and the model choice could be affected too.

**What I will do, fixed before looking at any corrected number.**
1. Add `final_answer_last()` (text after the last `<OUTPUT>` up to the next `</OUTPUT>`), and re-label with the same classifier prompts, the same repair rule and the same classifier models, only the cells where the two extractions differ (pilot and main). Unchanged cells keep their labels. Classifier B audits a seeded 25% of the re-labeled cells.
2. Recompute the pilot gaps with corrected labels and apply the model-choice rule again. If it would choose different models, I report that prominently; the main run is not repeated (it used the models and money already decided), and the report says the model choice rested on a flawed extraction.
3. Recompute every main-run result with corrected labels, with the registered analysis code unchanged. **Both versions are reported side by side**: "as run" (first-`<OUTPUT>` extraction) and "corrected" (last-`<OUTPUT>`). The corrected one follows the registered rule and is the one I treat as the result; I do not choose between them by which verdict looks better.
4. The regex flag and the sensitivity analyses are recomputed on the corrected answers.

**Not changed.** Prompts, models, calls, design G3, hypotheses, estimators, intervals, margin, classifier rubric. Cost of the re-labeling is a few tenths of a USD.

## Outcome (added after the corrected run; the plan above was not changed)
- Re-labeled cells: pilot 47, main 768 (classifier A), plus the seeded 25% audit by classifier B. First pass hit upstream rate limits (HTTP 429); those entries were discarded and redone at lower concurrency with the same prompts (a retry of an infrastructure error, not a new draw on content). Final: no missing labels among re-labeled cells. Extra cost about 0.14 USD usage, paid from credits already bought.
- Pilot: gaps unchanged to three decimals for all 8 candidates, so the model-choice rule gives the same two models.
- Main: Gemini unchanged. Qwen: mu 0.511 to 0.503, D -0.055 to -0.047 [-0.189, 0.093], H3 0.498 to 0.482 [0.298, 0.668], tau-hat 0.145 to 0.151. No verdict changed; kappa 0.96 on 1,957 audited outputs.
- Code: `harness/reclassify_v2.py`, `final_answer_last()` in `harness/common.py`, `AF_CORRECTED=1 python harness/analysis.py` writes `results/main_results_corrected.json`. `data/main_clf.jsonl` stays as run; `data/*_clf_v2.jsonl` holds the corrections.
- Remaining limit: some Qwen outputs have unclosed or nested tags; the last-`<OUTPUT>` rule is the registered meaning but a few replies still contain draft-like text.
