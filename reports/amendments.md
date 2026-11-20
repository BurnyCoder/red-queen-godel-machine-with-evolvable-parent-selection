# Prospective amendments

## 20 November 2026 · Manuscript cleaning before any model call

An audit of the registered training and validation inputs found publication mastheads joined to scientific text or a page number by PDF extraction. Some titles also contained the literal double-blind review masthead. The original cleaner missed those cases. We removed the boundary assumption, stripped the blind-review masthead and handled whitespace in OpenReview URL prefixes. We preserved surrounding manuscript text and phrases such as “final decision” when they describe a scientific task. The source CSV, grouping rules, sampling seed, methods and statistical decision rule retain their registered definitions. The current split file fingerprints the corrected text. The original Git commit preserves the previous fingerprints. The audit used no model predictions or sealed test outcomes. [Original manifest](https://github.com/BurnyCoder/red-queen-godel-machine-with-evolvable-parent-selection/blob/5454789/results/split-manifest.json) · [Current manifest](../results/split-manifest.json) · [Cleaner](../src/rqstudy/data.py)

The operational cap on retries and groupwise end-of-week reserve were specified before inference. [Operational rules](operational-rules.md)
