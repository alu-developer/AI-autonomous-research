# Framework research notes (handoff for future build sessions)

Purpose: everything learned in the Nov 2026 literature review that matters for BUILDING the framework. Read this before designing or coding. `blueprint.md` is the short version; this file is the detailed one. Claims below come from the sources in section 8; "(case study)" means a single report, not an established result.

## 1. Reference systems and what to borrow

### AI Scientist v1/v2 (Sakana AI, UBC, Vector, Oxford; Nature 651, 914, March 2026)
- Pipeline: idea -> code -> experiments -> plots/analysis -> full manuscript -> own peer review.
- v1 needed human code templates. v2 is template-free, uses **progressive agentic tree search** run by an **experiment-manager agent**, plus a **VLM feedback loop** that critiques figures.
- v2 had one of three fully AI-generated papers accepted at an ICLR workshop (ICLR 2025 "I Can't Believe It's Not Better"), under IRB approval and with organizer cooperation.
- Stated limits: verifying outputs is time-intensive; weak at genuinely novel, high-impact hypotheses; weak at justifying design decisions with domain expertise. Only computer science so far.
- Open code: github.com/SakanaAI/AI-Scientist-v2. Search is configured in `bfts_config.yaml` (`num_workers` parallel paths, `steps` max nodes). Optional Semantic Scholar key for literature search.
- Borrow: tree search over experiment attempts, an experiment-manager role, figure critique, separating ideation JSON from the run stage.

### Google AI Co-Scientist (Gemini; blog Feb 2025; Nature + DeepMind post May 2026)
- Hypothesis-generation system. Agents: Generation, Reflection, Ranking, Evolution, Proximity, Meta-review, coordinated by a **Supervisor** that parses the goal into a research-plan configuration and decides how often to run each agent and when to stop.
- Mechanisms: self-play scientific debate, **tournament ranking with an Elo-style metric**, an evolution step that refines top hypotheses, a Reflection agent that first reviews without web search, then against literature. Uses tools (web search, specialized models). Scales test-time compute.
- Validated in real labs (drug repurposing, target discovery, antimicrobial-resistance mechanisms) with expert-in-the-loop guidance.
- Borrow: supervisor + role agents, pairwise tournament ranking, Elo as an automatic quality proxy, reflection in two passes (no-search, then literature-grounded), human feedback hooks.

### AlphaEvolve (Google DeepMind; arXiv:2506.13131; math follow-up arXiv:2511.02864 with Terence Tao)
- Evolutionary coding agent: LLMs propose code changes, **automated evaluators** score them, a program database drives which programs seed the next round. Can evolve whole codebases, not only single functions.
- Works where progress is machine-checkable (math, algorithms, kernels, scheduling). Found provably correct algorithms beating the state of the art on several problems and improved real Google infrastructure.
- Borrow: evaluator-first design, a program/candidate database, evolutionary selection, human-readable outputs for debuggability.

### Others noted
- Agent Laboratory (open-source AI scientist system; audited together with AI Scientist-v2 in the NeurIPS 2025 paper, section 3).
- "Deep Research" interactive multi-agent system (arXiv:2601.12542): planning, data analysis, literature search and novelty-detection agents on a **persistent world state**; turnaround in minutes so a human can steer.
- Lossfunk four-attempt case study (arXiv:2601.03315): six-agent pipeline (idea, hypotheses, experiment plan, output evaluation, outline, revision) with Claude Code executing plans; context kept in shared files (`idea.md`, `hypotheses.md`, `plan.md`, `agent.md`, `code_logs.md`, `paper_outline.md`).
- Survey of AI Scientists (arXiv:2510.23045) for a taxonomy.

## 2. Cross-cutting design lessons
1. **Evaluator first.** The system is only as good as its ability to check results automatically. Pick domains with ground-truth checks first.
2. **Search, not a single pass.** Tree search, evolution and tournaments all outperform linear pipelines in the cited systems.
3. **Role separation plus a supervisor.** Generator, critic, ranker, experimenter, manager are separate agents with separate prompts and ideally separate contexts.
4. **Persistent shared state.** Files in a git repo are the memory; agents must re-ground from them.
5. **Human gates where verification is weak.** No claim leaves the system without human review.
6. **Spend compute on diversity and verification, not on longer single chains.**

## 3. Failure modes and required countermeasures
From the Lossfunk case study (single report): (a) defaults to training-data libraries/datasets over explicit instructions, (b) implementation drift under timeouts, (c) context and memory degradation on long tasks, (d) overstates success, (e) lacks tacit domain expertise for baselines and validity checks, (f) weak scientific taste (single seeds, infeasible compute).
Its design principles: start abstract and ground later; verify everything with critics that read **raw outputs**; plan for failure and recovery (modular steps, separate code generation from execution, prespecified recovery); log everything.

From Luo, Kasirzadeh, Shah (NeurIPS 2025, audit of Agent Laboratory and AI Scientist-v2): four methodological pitfalls: **inappropriate benchmark selection** (favored benchmarks where prior SOTA was strong, or defaulted to the first options listed), **data leakage**, **metric misuse**, **post-hoc selection bias**. Recommendation: require trace logs and code of the whole automated process with any submission.

Implementation checklist derived from the above (design decisions, not claims from the papers):
- Preregister benchmark, metric, seeds and baselines in a spec file before a run; the experimenter may not change it.
- Randomize or hash-order candidate benchmarks rather than letting the agent choose.
- Run every candidate with N>=3 seeds; report all runs, including failures.
- Critic agent receives raw logs and diffs against the spec, never the experimenter's summary.
- Pin dependency versions and dataset versions in the plan; fail the run if they differ.
- Use held-out test data the agents cannot read.
- Run history is append-only in `runs/`.

## 4. Evaluation of the framework itself
- **Replication benchmarks:** PaperBench (replicate ICML-level papers from scratch; arXiv:2504.01848), ReplicationBench (astrophysics; arXiv:2510.24591), CORE-Bench, RExBench (extend existing research; agents still need substantial human guidance; arXiv:2506.22598).
- **ML engineering / R&D:** RE-Bench (7 open-ended ML research-engineering tasks vs human experts; a significant gap to top humans remained in most environments; arXiv:2411.15114), MLE-bench (Kaggle-style), MLRC-Bench (open research problems; arXiv:2504.09702).
- Use these to compare against baselines before trusting the system on open-ended problems. Leaderboard numbers change quickly, so re-check them at build time.

## 5. Proposed architecture (to be validated in the build)
```
Supervisor
 |- Ideator        -> candidate hypotheses (structured JSON)
 |- Critic/Reflect -> two passes: no-search sanity, then literature-grounded
 |- Ranker         -> pairwise tournament, Elo scores
 |- Experimenter   -> tree search over implementations; runs code in a sandbox
 |- Verifier       -> domain evaluator + independent raw-output critic
 |- Archivist      -> writes run logs, decision log, final report
Shared state: repo files (spec.md, hypotheses.json, plan.md, runs/<id>/...)
Human gate: before any result is reported as a finding
```

## 6. Suggested build order
1. Pick the first domain with an automatic verifier (candidates: combinatorial/math constructions, algorithm optimization, replication of a small ML paper). Decision pending with the user.
2. Write the verifier and a tiny benchmark in `evals/` and test it.
3. Minimal loop: Ideator -> Experimenter -> Verifier on one problem, full logging into `runs/`.
4. Add Critic and Ranker (Elo tournament).
5. Add search (tree or evolutionary) with a candidate database.
6. Run a replication benchmark subset; compare to published baselines.
7. Only then try open-ended problems, with the human gate on.

## 7. Open questions
- First domain? Compute budget (the cloud workspace has no GPU, limited network)? Which model provider and budget per run?
- Where do experiments run: cloud sandbox vs the user's computer?
- How strict should the human gate be?

## 8. Sources
- Lu, Lu, Lange, Yamada, Hu, Foerster, Ha, Clune (2026). Towards end-to-end automation of AI research. Nature 651, 914-919. arXiv:2606.15497. https://arxiv.org/abs/2606.15497
- Yamada et al. (2025). The AI Scientist-v2. https://arxiv.org/abs/2504.08066 ; code https://github.com/SakanaAI/AI-Scientist-v2
- Gottweis, Natarajan (2025). Accelerating scientific breakthroughs with an AI co-scientist. https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/
- Co-Scientist (Nature, May 2026). https://deepmind.google/blog/co-scientist-a-multi-agent-ai-partner-to-accelerate-research/
- Novikov et al. (2025). AlphaEvolve. https://arxiv.org/abs/2506.13131 ; blog https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- Georgiev, Gomez-Serrano, Tao, Wagner (2025). Mathematical exploration and discovery at scale. https://arxiv.org/abs/2511.02864
- Trehan, Chopra (2026). Why LLMs Aren't Scientists Yet. https://arxiv.org/abs/2601.03315 ; artefacts https://github.com/Lossfunk/ai-scientist-artefacts-v1
- Luo, Kasirzadeh, Shah (2025). The More You Automate, the Less You See. NeurIPS 2025. https://arxiv.org/abs/2509.08713
- Weidener et al. (2026). Rethinking the AI Scientist: Interactive Multi-Agent Workflows. https://arxiv.org/abs/2601.12542
- Survey of AI Scientists. https://arxiv.org/abs/2510.23045
- Starace et al. (2025). PaperBench. https://arxiv.org/abs/2504.01848
- Wijk et al. (2024). RE-Bench. https://arxiv.org/abs/2411.15114
- RExBench. https://arxiv.org/abs/2506.22598
- MLRC-Bench. https://arxiv.org/abs/2504.09702
- ReplicationBench. https://arxiv.org/abs/2510.24591

Note on provenance: this review was done from search snippets and one fetched paper (arXiv:2601.03315), not full reads of every paper. Verify specifics (numbers, exact mechanisms) in the primary sources before depending on them.
