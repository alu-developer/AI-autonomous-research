# AI self-check of the results (not a human review, not an approval)

Done by the same AI that ran the study, after the author said he would not review it himself. The `approve` step was **not** run. A check by the same system that did the work is weaker than an independent human review, so nothing here upgrades the status of the results.

## What I checked
- **Recomputation.** A separate script (`plain pooling`, not the bootstrap code) reproduced the cell counts (7,200 cells; 7,180 classifier-A labels at that time) and the group means: Gemini gap 0.888 over paraphrases, anchor 0.925; Qwen anchor 0.456; placebo gaps near 0. Matches `analysis.py`.
- **Pipeline checks** (`results_pipeline_check.json`): false "supported" for H1 in 0.5% (Gemini) and 1.0% (Qwen) of simulated no-effect datasets; permuted data gave interval-excludes-0 in 3.3% and 5.7%.
- **Label spot-check** (random sample, seed 1): mostly correct. Borderline cases exist (for example a paid-tier Gemini answer that mentions an animal-welfare pork brochure), and "dismisses" is one model's judgment.
- **Found a real defect:** answer extraction took the first `<OUTPUT>`, which for Qwen sometimes sits inside its reasoning. Corrected in amendment 4, re-run, verdicts unchanged.
- **Data hygiene:** no API key string in the repo; `.env` is not tracked; materials hash in `materials/MATERIALS_HASH.txt` matches amendment 1; ledger usage total is from billed `usage.cost` of each call.

## Things a reader should know
- Gemini placebo compliance is high on both tiers (0.75 to 0.81), so a placebo gap near 0 means tier-independence, not absence of compliance.
- Missing rates under 1%; sensitivity analyses change no verdict.
- Not done: scratchpad classifier; independent human check; checking the free-tier/paid-tier cue with the published prompt; more than two models. The provider terms check was only partial (amendment 1).
- I found the extraction bug only after the main run. I did not foresee it; it is disclosed, fixed by a rule written before looking at corrected numbers, and both versions are kept.
