# Candidate research topics (2026-11-20, first pass)

Method: importance / neglectedness / tractability (the framework used by Open Philanthropy and 80,000 Hours), plus two filters specific to this project: (1) can an AI agent with ~70 EUR/month, no GPU and no lab do real work on it, (2) is there a way to verify the work automatically. Scores are Claude's rough judgment, not measurements. All "facts" come from the sources listed at the end and must be re-checked before anyone acts on them.

## Ranked list

| # | Topic | Importance | Neglected | AI-doable here | Verifiable |
|---|---|---|---|---|---|
| 1 | Reproduction and robustness audits of studies that drive big funding decisions (development economics, global health) | medium-high (indirect, multiplies other work) | high | high | high (numbers can be compared to published ones) |
| 2 | Evidence-gap and assumption checks for cost-effectiveness analyses (GiveWell-style open questions) | high | medium | medium | low-medium |
| 3 | Quantitative importance/neglectedness mapping of R&D targets (vaccines, diagnostics, drugs) | high | medium-high | medium-high | medium |
| 4 | Childhood lead exposure: source attribution and evidence gaps | high | high | low-medium (bottleneck is field measurement) | medium |
| 5 | Antimicrobial resistance burden under sparse data | high | medium | low-medium | low |
| 6 | Global priorities research itself (comparing cause areas rigorously) | very high | high | low | low |
| 7 | Math and algorithm discovery with machine-checkable scores | low direct impact | n/a | very high | very high |
| 8 | AI safety research done by AI | very high | medium | unclear, risky | low |

## Notes per topic
1. Two 2026 papers show agents can largely recover published social-science results (ETH Zurich: 48 papers) and one workflow ran over 4,452 replication packages from five economics journals (Harvard/MIT). Authors note that AI lowers the cost of producing papers faster than the cost of checking them. Weakness: agents struggle to retrieve new data for true replications (ReplicatorBench). Best first project: cheap, verifiable, directly attacks the verification bottleneck this whole field has. Target the studies behind major funding decisions, not random papers.
2. GiveWell publishes open research questions (e.g. how to value averting morbidity vs increasing consumption; size of non-mortality benefits). AI can gather and structure evidence, but a 2025 systematic review found current evidence does not support GenAI in evidence synthesis without human oversight (substantial mistakes). Needs a human gate and independent checking.
3. Open Philanthropy found R&D funding varies 10x or more across infectious diseases, and flagged group A streptococcus, hepatitis C and syphilis as low-funded relative to burden. This kind of analysis (burden data + funding data) can be repeated and extended by an agent with public data.
4. CGD working group: lead poisoning affects roughly 1 in 3 children globally; funding identified was only about 11 million USD per year; World Bank estimates the burden at 4.6 to 5 trillion USD per year. Rethink Priorities: 21.7M DALYs vs 46.4M for malaria. Main open question: which sources (paint, spices, batteries, cookware) contribute how much. Agents can synthesize existing data, but the key evidence needs measurements.
5. About 5.0M deaths associated with AMR per year, 4.3M in LMICs (2021 estimates); surveillance data are sparse and unrepresentative in LMICs, which limits what an AI can verify.
6. 80,000 Hours notes there is little research guiding the highest-level priorities. Important but hard to verify; an agent could help with structured comparison, not with deciding values.
7. OpenEvolve-family tools fit directly. Good for testing the pipeline, not for impact.
8. Dual-use and self-improvement risks; do not run autonomously. Human-led only.

## Which frameworks help (decision logic)
- Topic 1: no big framework needed. A coding agent + a verifier script that compares reproduced numbers with published tables. Reuse open code from the ETH paper (arXiv:2604.21965), ReplicatorBench (Center for Open Science), and the Harvard/MIT workflow.
- Topics 2-5: building blocks only (coding agent with science skills, literature tools). No framework provides problem choice, verification of claims, or protocol for evidence quality; those need a written review protocol and a human check.
- Topic 7: OpenEvolve / ShinkaEvolve / CodeEvolve.
- Not helpful for any of the top topics: AI Scientist-v2 and autoresearch (GPU ML experiments).

## Sources
- CGD lead working group: https://www.cgdev.org/node/3132868 ; https://www.cgdev.org/node/3136411
- Rethink Priorities lead report: https://forum.effectivealtruism.org/posts/naTwu3xD3WFWu5fbp
- Open Philanthropy vaccine funding: https://www.coefficientgiving.org/research/a-quantitative-approach-to-vaccine-funding/
- GiveWell "Research I'd like to see": https://forum.effectivealtruism.org/posts/2TcdiAFSTuS6jBvNL/research-i-d-like-to-see-1 ; cross-cutting strategy: https://blog.givewell.org/2024/12/18/research-strategy-cross-cutting/
- AMR: https://pmc.ncbi.nlm.nih.gov/articles/PMC7763986 ; https://ora.ox.ac.uk/objects/uuid:24fcbe42-ff93-4258-b3a5-0fb94e128936/files/rv692t8574
- Reproduction by agents: https://arxiv.org/html/2604.21965v1 ; https://economics.mit.edu/sites/default/files/2026-09/metascience.pdf ; https://arxiv.org/html/2602.11354v1 ; https://www.arxiv.org/pdf/2602.18453
- GenAI in evidence synthesis: https://resolve.cambridge.org/core/services/aop-cambridge-core/content/view/2DACF6D129AA6E46CB8A8740A03D0675/S175928792500016Xa.pdf/generative-artificial-intelligence-use-in-evidence-synthesis-a-systematic-review.pdf
- 80,000 Hours problem profiles: https://80000hours.org/problem-profiles/
