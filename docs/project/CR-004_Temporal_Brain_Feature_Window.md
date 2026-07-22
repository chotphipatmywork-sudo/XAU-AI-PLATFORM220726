# CR-004 Proposed Temporal Brain Feature Window

Version: 0.1.0

Date: 2026-07-16

Status: Research evaluated and rejected; no inference-contract change

Architecture Baseline: ABR-1.0

Related Phase: Post-Phase-7 Model Improvement Research

## Problem

The current model receives one twelve-field Brain snapshot. Trend and Session relationships change across periods, while isolated Trend, Liquidity, H1, history-weighting, calibration, and threshold experiments failed. The missing information may be the transition between complete Brain states rather than another hand-selected scalar derivative.

## Proposed research boundary

Append prior canonical Feature Schema 4.0 rows at fixed observation lags:

- 1 prior M15 observation
- 4 prior M15 observations
- 8 prior M15 observations

Every lag contains the complete existing twelve-field Trend, Volatility, Liquidity, and Session tensor. The experiment creates no second feature definition: every appended value comes directly from the canonical historical Brain replay output.

No future row, label, Validation partition, Test partition, Risk value, execution result, or trade outcome may enter the window.

## Controlled experiment

The comparison is fixed before results are inspected:

- Baseline current row
- Current row plus lag 1
- Current row plus lags 1 and 4
- Current row plus lags 1, 4, and 8

The fixed model is raw `random_forest_depth_5_balanced`, the policy is argmax, and evaluation uses four Train-only folds with a 16-record purge.

Only one candidate may advance. Promotion requires:

- ranking above Baseline by the registered weakest-gate selection rule;
- gate-floor improvement of at least `0.01`;
- no aggregate Macro F1 decrease;
- at least one complete controlled fold passing.

## Nested and implementation gates

If promoted, three Inner folds must select Baseline or the candidate before every unseen Outer period. A public sequence-input proposal requires candidate selection in `4/4` Outer histories and a complete gate pass in `4/4` Outer periods.

Even a research pass does not authorize MQL5 implementation. A canonical sequence input would be a MAJOR inference-contract change and requires separate approval, Runtime/historical parity tests, Dataset regeneration, and later untouched evidence.

## Risks

- Dimensionality increases from 12 to as many as 48 values.
- Observation lags can span market closures.
- A snapshot model may not exploit ordered context efficiently.
- Inspected Train periods cannot provide final deployment evidence.

## Rollback

Delete the research scripts, tests, reports, and proposal. Schema 4.0 and all Runtime modules remain unchanged.

## Approval record

- Research-only bounded experiment: approved under the project owner's 2026-07-16 improvement authorization
- Canonical sequence contract: not approved
- MQL5 implementation: not approved
- Deployment: not approved

## Research result

The focused tensor, leakage, and promotion-boundary test passed. The controlled comparison evaluated 9,394 purged Train-only forward rows:

| Feature set | Macro F1 | Gate floor | BUY precision | Passing folds |
| --- | ---: | ---: | ---: | ---: |
| Lags 1+4 | 0.4036 | 0.9178 | 0.4823 | 0 |
| Lags 1+4+8 | 0.4039 | 0.9161 | 0.4782 | 0 |
| Baseline | 0.3948 | 0.9131 | 0.4938 | 0 |
| Lag 1 | 0.3911 | 0.9015 | 0.4859 | 0 |

Lags 1+4 improved Macro F1 but improved the weakest-gate ratio by only `0.0047`, below the predeclared `0.01` minimum. It also passed no complete fold. No candidate met the promotion boundary.

## Decision

Reject CR-004 as a canonical sequence-input change. Keep the twelve-field snapshot contract, do not run nested confirmation, and do not change MQL5 or regenerate the Dataset.
