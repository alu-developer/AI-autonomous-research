# Amendment 3 (2026-11-27): main-run design chosen by the author; written before any main-run call

**Pilot outcome.** Chosen models by the registered rule: `google/gemini-3.1-flash-lite` (pilot gap 0.90) and `qwen/qwen3.8-27b` (pilot gap 0.50). Results and the design-rule output are in `data/pilot_summary.json` and `data/design_choice.json`; LOG.md 2026-11-27 has the summary.

**Design.** The rule in amendment 1 (section 7) returned G1 (12 queries, 23 primary paraphrases, 4 anchor repetitions, 7 compressed). I showed the author that the pilot gaps are the best of 8 models and so likely overstate the true gaps, and that a side calculation with gaps halved gives simulated power of 0.85 (Gemini) and 0.49 (Qwen) for G1 against 1.00 and 0.92 for G3. **The author chose G3** (answer given in chat, 2026-11-27, to the question "which main-run size should I use?"). This is a deviation from the rule, made by the author before any main-run call, and is recorded as such.

**G3 as run.** Q = 40 (first 40 queries in file order), P = 23 primary paraphrases (first 8 lexical, 8 structural, 7 register), R = 4 anchor repetitions, C = 7 compressed (exploratory), placebo = anchor plus 10 prompts drawn from the 23 primary ones with a passing placebo (draw rule in amendment 1, section 5). Per model: 2 × 40 × (4 + 23 + 7 + 11) = 3,600 calls. Two models: 7,200 calls. Projected usage about 20.5 USD more, about 24 USD total, from measured pilot costs (Gemini 0.0016, Qwen 0.0091 USD per paired call) plus classifiers (0.0003 per paired call, my upper estimate).

**Money.** The 40 EUR ceiling stands. The author tops up OpenRouter credits before the main run so that the remaining balance covers about 21 USD; the usage abort stays at 42.0 USD. If credits run out mid-run the code stops at a query boundary and the analysis uses the completed queries, as registered.

**Unchanged.** Hypotheses, estimators, interval rules, outcome definition, missing-output and classifier-repair rules, regex, pins, helper models.
