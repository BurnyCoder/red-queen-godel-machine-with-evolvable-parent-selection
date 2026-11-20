# Run matrix

All arms use frozen local Qwen3.5-4B and the same paper split, anchor, context, evaluator replacement and editor budget. The sole arm-specific intervention is the expansion parent's selection mechanism. [Registration and decision rules](preregistration.md)

| Stage | Seeds | Arm | Scheduled validation per run | Endpoint set |
|---|---|---|---|---|
| Root | 0 | Initial program, no search | 0 | Pilot first; sealed root after freeze |
| Pilot | 0 | Editable, native clade, uniform, released handcrafted | 64 | 24 pilot-only manuscripts |
| Confirmatory primary | 1–8 | Editable and native clade | Common timing-selected budget from 64, 128, 256 | Same 100 sealed manuscripts |
| Secondary comparison | 1–5 | Fixed uniform and fixed handcrafted | Same budget | Same 100 |
| Midpoint intervention | 1 | Continuation of editable state with native override | Remaining half of common budget | Same 100 |
| Historical formula replay | All expansions | Released exponential vs paper reciprocal penalty | No model calls | Parent-ID disagreement |

The live dashboard displays training/search validation only. The first search meeting a stopping budget is archived with its endpoint, then independently evaluated on the correct evaluation split. All confirmatory endpoints are jointly frozen before access to test examples. Store a complete audit trail for unsuccessful edits. Generate score tables, plots and trajectory summaries directly from the raw run files.
