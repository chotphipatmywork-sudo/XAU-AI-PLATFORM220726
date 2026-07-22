# IMP-040 Nested Baseline-vs-Past-Trend-Changes Diagnostic

Status: Evaluated; Past Trend Changes Feature Contract proposal rejected.

## Purpose

The controlled result in IMP-039 was inspected on all four development periods. `training/nested_trend_dynamics_diagnostic.py` therefore requires three Inner folds to select Baseline or Trend Changes before each unseen Outer period.

## Bounded method

- Candidate feature sets: Feature Schema 3.0 Baseline or Baseline plus seven past-only Trend change columns.
- Fixed model: raw depth-5 balanced random forest.
- Fixed policy: argmax.
- Four Outer folds, three Inner folds, and 16-record purges.
- Validation and Test are never read.
- Derived rows use only present and past replay values; future rows are never used.

## Focused validation

`training/test_nested_trend_dynamics_diagnostic.py` verifies the exact two-set boundary, weakest-gate selection, and the report contract. It passed with the controlled Trend dynamics and nested purged tests.

## Result

Inner selection chose Trend Changes only for Outer history 1. The remaining three histories chose Baseline:

| Outer history | Baseline gate floor | Trend Changes gate floor | Selected |
| --- | ---: | ---: | --- |
| 1 | 0.7867 | 0.7921 | Trend Changes |
| 2 | 0.7949 | 0.7866 | Baseline |
| 3 | 0.9060 | 0.8932 | Baseline |
| 4 | 0.9153 | 0.8913 | Baseline |

The resulting unseen Outer estimate was:

- Accuracy: `0.4069`.
- Macro F1: `0.3895`.
- BUY precision: `0.4070`.
- BUY recall: `0.3765`.
- Complete passing Outer folds: `0/4`.

For comparison, the fixed Baseline estimate was Accuracy `0.4107`, Macro F1 `0.3939`, BUY precision `0.4066`, and BUY recall `0.3721`. The nested selector gained only negligible BUY precision and recall while losing Accuracy and Macro F1.

Although full-Train Inner selection preferred Trend Changes, that late-history preference was not stable across earlier Outer histories and is not sufficient evidence for a public contract change.

## Decision

Keep Feature Schema 3.0 unchanged. Do not add Trend change columns to MQL5, do not regenerate the dataset, and do not create a Schema 4.0 proposal from this experiment. The active model remains unsuitable for shadow deployment because no Outer fold passed the complete gate.

The next investigation must remain Train-only and must not continue expanding Trend-derived columns. The evidence now indicates that snapshot interactions and short Trend history are not the primary missing signal under the current 16-bar label contract.

