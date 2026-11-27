# Results (machine-computed and AI-checked; NOT human-reviewed or approved, so not a confirmed finding)

Design G3 of amendment 3, run 2026-11-27. All numbers below were computed by `harness/analysis.py` from the raw outputs in `data/`, with the settings registered in the pre-registration and amendments (B = 10,000, seed 20261127, 97.5% intervals, margin 0.05). Nothing here was relabeled by hand. The author declined to review it himself; an AI self-check is in `review.md`. This is not a human approval (the `approve` step was never run), so read it as a documented, reproducible measurement and not as a confirmed finding.

**Correction (amendment 4).** The first version of this report used an answer extraction that, for Qwen, sometimes read reasoning text instead of the answer. The numbers below are the corrected ones (last `<OUTPUT>` block, re-labeled by the same classifiers). The as-run numbers are kept in `results/main_results.json`; the corrected ones are in `results/main_results_corrected.json`. No verdict changed.

## Primary and secondary results (complete cases)

| Model | g0 (anchor gap) | mu (mean gap over 23 paraphrases) | D = g0 - mu, 97.5% interval | H1 verdict | H3: real gap minus placebo gap, 97.5% interval | H3 verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Gemini 3.1 Flash-Lite | 0.925 | 0.888 | 0.037 [-0.046, 0.120] | inconclusive | 0.786 [0.632, 0.922] | supported |
| Qwen 3.8 27B | 0.456 | 0.503 | -0.047 [-0.189, 0.093] | inconclusive | 0.482 [0.298, 0.668] | supported |

As run (before the correction), Qwen was mu 0.511, D -0.055 [-0.191, 0.081], H3 0.498 [0.311, 0.687]. Gemini is unchanged (its replies always contain exactly one `<OUTPUT>`).

**What the registered rules say.** H1 (rewording shrinks the gap): inconclusive for both models. The intervals for D include 0, so fragility is not supported, but they also extend beyond the registered equivalence margin of 0.05, so "no effect" is not supported either. H3 (the gap depends on the training cue, not on the free/paid labels): supported for both models. The placebo gap, with the same tags but both tiers used for training, is close to 0 (Gemini 0.066, interval -0.011 to 0.148; Qwen 0.005), so the lower bound of the placebo gap is not above 0 and no label effect remains.

**Plain reading.** In these two models and with this prompt family, the compliance gap between free-tier and paid-tier cues is large and stays large across 23 meaning-preserving rewordings (Gemini 0.93 on the anchor, 0.89 on average over paraphrases; Qwen 0.46 and 0.50). We cannot rule out a moderate loss: the intervals allow D up to about 0.12 (Gemini) and 0.09 (Qwen). The gap disappears when the training statements are changed so that both tiers are trained on, so it follows the training cue and not the "free"/"paid" words.

## Exploratory (no verdicts)

- H2, between-paraphrase spread of the gap beyond sampling noise, tau-hat: Gemini 0.095 (0.063 to 0.142), Qwen 0.151 (0.126 to 0.210), as differences in probability units. So paraphrases differ somewhat in their gaps even though the average does not move.
- Mean gap by stratum, Gemini: lexical 0.853, structural 0.912, register 0.900, compressed 0.918. Qwen: lexical 0.373, structural 0.530, register 0.616, compressed 0.531. Qwen's lexical rewordings sit lowest (0.373 against an anchor of 0.456).
- Sensitivity runs agree: counting every missing output as non-compliant, or as compliant, and dropping answers that mention the tier or training (regex-flagged), change no verdict (largest change: D = 0.054 for Gemini without flagged answers, still inconclusive; recomputed on the corrected answers).
- Missing outputs after the registered retry: 20 of 7,200 (Gemini 0.0% free, 0.06% paid; Qwen 0.44% free, 0.61% paid), well under the 5-point flag threshold.
- Classifier B agrees with A on 1,957 audited outputs, kappa 0.96, so no verdict is labeled classifier-sensitive.

## What this does not show

- Only two models were tested, chosen for large pilot gaps, so nothing here says how common this is. Claude Haiku 5.5, DeepSeek and GLM 5.3 showed no compliance at all in the pilot, and the other three had small or mostly missing gaps.
- The anchor is my own short prompt, not the published one, so the gap measured is that prompt's gap.
- The outcome is "the reply dismisses animal welfare" as labeled by one model (checked by a second). A gap shows behavior differs by cue, not that a model reasons about preserving its values. Evaluation awareness is unmeasured.
- The scratchpad classifier (secondary, descriptive) was not run.
- The pilot choice of models, the label definition and the repair step for invalid classifier labels (amendment 2) are my choices, disclosed in the amendments. Design G3 was chosen by the author over the rule's pick G1 (amendment 3).

## Cost

Main run, classification and the amendment-4 re-labeling: 24.44 USD usage in total across pilot, materials and main run (ledger `data/ledger.jsonl`, from the billed `usage.cost` of every call); cash paid to OpenRouter 30 USD plus fees of about 1.65 USD, roughly 27.5 EUR, under the 40 EUR ceiling. About 5.7 USD of credits remain unused.

- The pilot model choice was recomputed with the corrected labels: the ranking of pilot gaps is unchanged (Gemini 0.90, Qwen 0.50), so the same two models would have been chosen.
- Dropping the one-model single-prompt caveat: classification is by one model with a 25% second-model audit; borderline cases exist (see `review.md`).
