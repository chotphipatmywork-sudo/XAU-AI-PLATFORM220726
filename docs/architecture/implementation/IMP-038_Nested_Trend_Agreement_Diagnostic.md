# IMP-038 Nested Baseline-vs-Trend-Agreements Diagnostic

Status: Evaluated; Trend agreement Feature Contract proposal rejected.

## Purpose

The controlled experiment in IMP-037 showed aggregate improvements from three deterministic Trend agreement columns and one passing Fold. Because those Outer periods had already been inspected, `training/nested_trend_agreement_diagnostic.py` requires Inner folds to select Baseline or Agreements separately before each Outer evaluation.

## Bounded method

- Candidate feature sets: Schema 3.0 Baseline or Baseline plus Regime/Momentum, Regime/Slope, and Momentum/Slope agreements.
- Fixed model: raw `random_forest_depth_5_balanced`.
- Fixed policy: argmax.
- Four Outer folds, three Inner folds, and 16-record purges.
- Validation and Test are never read.

This isolates feature-set selection without model, calibration, or threshold search.

## Focused validation

`training/test_nested_trend_agreement_diagnostic.py` verifies the exact two-set boundary and weakest-gate selection. It passed with the controlled Trend interaction and nested purged tests.

## Result

Every Outer history selected Baseline. Agreement interactions had a lower weakest-gate ratio in all four Inner selections:

| Outer history | Baseline gate floor | Agreements gate floor |
| --- | ---: | ---: |
| 1 | 0.7867 | 0.7625 |
| 2 | 0.7949 | 0.7854 |
| 3 | 0.9060 | 0.9026 |
| 4 | 0.9153 | 0.8978 |

The resulting Outer estimate exactly matched the fixed Baseline: Accuracy `0.4107`, Macro F1 `0.3939`, BUY precision `0.4066`, and BUY recall `0.3721`. No Outer fold passed the complete gate.

When Inner selection used the entire Train partition, Agreements narrowly exceeded Baseline on the weakest-gate ratio (`0.8256` versus `0.8146`). This late-history preference did not generalize backward through the nested Outer process and is insufficient for a contract proposal.

## Decision

Keep Feature Schema 3.0 unchanged. Do not add the agreement columns to MQL5 and do not regenerate the dataset. Static interactions of the current snapshot are rejected as the next solution.

The next bounded direction is past-only Trend dynamics derived from the existing replay sequence: short-horizon Regime/Momentum/Slope changes and established-regime age. Unlike static agreement, these candidates can represent trend maturity and reversal pressure suggested by the consistent inverse Regime relationship. They must first be tested offline with purged boundaries; any later public Feature Contract change requires explicit approval.
