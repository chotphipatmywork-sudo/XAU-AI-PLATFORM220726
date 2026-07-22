# IMP-039 Past-only Trend Dynamics Diagnostic

Status: Controlled Train-only experiment evaluated; bounded nested confirmation required.

## Purpose

IMP-038 rejected static Trend agreement columns. `training/trend_dynamics_diagnostic.py` tests whether recent changes in the existing replayed Brain Trend sequence carry more temporally stable information than the current snapshot alone.

## Candidate dynamics

All candidates are deterministic, bounded to `0..100`, and use only the current row and earlier rows:

- Trend Regime changes over 1, 4, and 8 bars.
- Trend Momentum changes over 1 and 4 bars.
- Trend Slope changes over 1 and 4 bars.
- Regime age over the previous 16 bars.

No future row, label, Validation partition, or Test partition is used. These columns are offline diagnostics and are not active Feature Schema 3.0 inputs.

## Fixed comparison

- Model: raw depth-5 balanced random forest.
- Policy: argmax.
- History: expanding.
- Evaluation: four chronological Train-only periods with a 16-record purge.
- Variable under test: the appended dynamics feature set only.

## Focused validation

`training/test_trend_dynamics_diagnostic.py` verifies delta direction, bounded outputs, regime-age behavior, feature-set indices, and future-row isolation. Mutating later rows cannot change previously derived values. The test passed.

## Result

The seven-column `change_only` set ranked first in the controlled comparison:

| Feature set | Accuracy | Macro F1 | BUY precision | BUY recall | Passed folds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Trend changes | 0.4249 | 0.4037 | 0.4303 | 0.4000 | 0 |
| Baseline | 0.4107 | 0.3939 | 0.4066 | 0.3721 | 0 |

Trend changes improved Macro F1 in three of four periods, but degraded the first period and did not pass the complete gate in any period. Regime age alone ranked below Baseline.

## Decision

Do not change Feature Schema 3.0 from this controlled result. Advance only `change_only` to a bounded nested Baseline-vs-Trend-Changes confirmation. Model and policy must remain fixed so that the experiment isolates feature-set selection.

IMP-040 completed the nested confirmation and rejected the Feature Contract proposal.

