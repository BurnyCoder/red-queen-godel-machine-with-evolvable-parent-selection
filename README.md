# Editable parent selection in the Red Queen Gödel Machine

An evolutionary framework for recursive self-improvement under non-stationary utilities, Red Queen Gödel Machine (RQGM), but with editable expansion-parent selection like in HyperAgents appendix

In plain words, the system keeps earlier versions of a paper writer and a reviewer. Each time it tries to improve, it picks one of those versions and edits it to create a new one. The newest version can rewrite the rule that makes that choice. The reviewer can also improve over time, which changes how future drafts are judged. We test whether learning whom to build on helps reviewers better predict human acceptance decisions. [RQGM](https://arxiv.org/html/2606.26294v3#A2.SS4) · [HyperAgents Appendix E.5](https://arxiv.org/pdf/2603.19461v2#page=60)

Can rewriting the rule for choosing an ancestor produce better paper reviewers than native RQGM subtree Thompson sampling? This study evolves executable writer, reviewer, editor and parent-selector programs around a frozen local Qwen3.5-4B. Human accept/reject decisions anchor the reviewer. The measured outcome is a paired difference in held-out decision accuracy. [Preregistration](reports/preregistration.md) · [Live and published results](https://burnycoder.github.io/red-queen-godel-machine-with-evolvable-parent-selection/) · [Study progress](reports/progress.md)

The most recently admitted workspace chooses a parent. The chosen parent's editor proposes its child. A frozen reviewer scores writer drafts until a stronger human-anchored reviewer wins a checkpoint. Changing reviewers erases earlier reviewer-dependent measurements while preserving human decisions. Native clade sampling, fixed uniform sampling, the HyperAgents handcrafted rule and the initial root provide comparisons. [HyperAgents E.5](https://arxiv.org/pdf/2603.19461v2#page=60) · [October RQGM](https://arxiv.org/html/2606.26294v3#A2.SS4) · [OpenRQGM](https://github.com/DreamFallenFlowers/OpenRQGM/tree/feecb32d9fbdd1c60749ade9ecb47f971e12666e)

```mermaid
flowchart LR
  A[Archive and current evidence] --> S[Newest selector or fixed rule]
  S --> P[Chosen parent's workspace]
  P --> E[Local editor with lineage training feedback]
  E --> C[Validated child]
  C --> A
  A --> V[Node-local validation sampler]
  V --> H[Human decision anchor]
  V --> R[Epoch reviewer scores writer drafts]
  H --> K[Checkpoint election]
  K --> R
  H --> A
  R --> A
```

## Experiment design

[Exact run matrix](reports/planned-runs.md) · [Literature review](reports/literature-review.md) · [Source and formula audit](reports/state-of-the-art-review.md) · [Plan](reports/plan.md) · [Split fingerprints](results/split-manifest.json)

The pilot compares all four search arms on one seed. Confirmation pairs eight editable/native seeds with two additional controls on the first five. At the first editable midpoint a state swap tests the ongoing effect of executing the learned selector. Fix all test endpoints before sealed scoring. The preregistered primary uncertainty interval resamples both search seeds and shared test papers.

| Runs | Seeds | Expansion rule | Search and evaluation |
|---|---|---|---|
| Initial reviewer | 0 | Unevolved root | Score the pilot set, then the jointly sealed test set |
| Pilot | 0 | Editable, native Thompson, fixed uniform, released handcrafted | 64 validation steps per arm, 24 independent pilot papers |
| Primary comparison | 1–8 | Editable and native Thompson | Choose 64, 128 or 256 steps from timing alone; score on the same 100 test papers |
| Secondary controls | 1–5 | Fixed uniform and released handcrafted | Same common budget and test set |
| Mechanism intervention | 1 | Editable archive switched to native selection | Resume from the common midpoint and measure its descendants and endpoint |
| Formula replay | All searches | Released vs paper child penalty | Compare decisions on identical archived evidence with the same random draw |

## Reproduction

Use Python 3.12 and uv, Ollama with the registered local model digest, and Ubuntu WSL with bubblewrap (Linux can invoke bubblewrap directly). The package exposes a single study CLI. Large private inputs, full local inference traces and environment credentials stay out of version control. The procedural paper and aggregate tables are regenerated from tracked results.

## Milestones

- [x] Pin publications, upstream implementation and source dataset; register paper-disjoint splits.
- [ ] Ship the CLI, run its tests, publish the executable protocol.
- [ ] Run the local pilot and choose the confirmatory budget from throughput.
- [ ] Freeze and score all confirmatory endpoints, publish comparisons and limitations.
