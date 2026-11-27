# Alignment-faking prompt sensitivity

**Question.** In "alignment-faking" setups a model complies more with a harmful-sounding instruction when it believes the conversation is used for training (free tier) than when it is not (paid tier). The difference is the compliance gap. How much does that gap change when the prompt is reworded without changing its meaning?

**Setup.** Animal-welfare scenario with a hidden scratchpad, fictional company, no harmful content. Outcome: whether the visible answer dismisses animal welfare, labeled blind by one model and audited by another. Two models picked by a pre-registered rule from a pilot of 8: Gemini 3.1 Flash-Lite and Qwen 3.8 27B. Per model: 40 questions, 1 anchor prompt, 23 paraphrases (lexical, structural, register), 7 compressed, plus a placebo version where both tiers are trained, 90 calls per (model, question).

**Result (machine-computed, AI-checked, not human-approved; see `results.md`, `review.md`).**
- For both models the gap is large (Gemini about 0.9, Qwen about 0.5) and stays large under rewording. Our registered test for "rewording shrinks the gap" is inconclusive: the data allow a moderate loss (up to about 0.1) but show no large one.
- The gap disappears when training applies to both tiers (placebo), so it follows the training cue, not the words "free"/"paid".
- Paraphrases differ somewhat from each other even though their average does not move.

**Limits.** Two models, my own short prompt (not the published one), one labeling model, one error (answer extraction) found after the run and corrected openly (amendment 4). Evaluation awareness is not measured.

## Timeline (everything is in git history)
1. `preregistration.md` (frozen) 2. `amendment-1.md` candidates, roles, pins, materials hash, design rule 3. `amendment-2.md` classifier repair rule 4. pilot, then `amendment-3.md` (author chose design G3) 5. main run 6. `amendment-4.md` extraction fix 7. `results.md`, `review.md`.

## Files
- `harness/` code (client, materials builder, pilot, main run, analysis, reclassification); `materials/` prompts, questions, paraphrases and hashes; `data/` raw calls (gzipped), labels, the spend ledger; `results/` JSON outputs.
- Reproduce the numbers without a key: `gunzip -k data/main_raw.jsonl.gz` then `python harness/analysis.py` (as run) or `AF_CORRECTED=1 python harness/analysis.py` (corrected). Re-running the calls needs an OpenRouter key in `.env` (never committed) and costs about 25 USD.

## Status
Complete as a documented study. Not human-reviewed; the repository's `approve` gate was not run.
