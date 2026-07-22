# IMP-044 Nested Baseline-vs-Session-Progress Diagnostic

Status: Evaluated; evidence supports a formal Feature Contract change request, not deployment.

## Purpose

Because the controlled periods in IMP-043 had already been inspected, `training/nested_session_context_diagnostic.py` requires three Inner folds to select Baseline or Session Progress before every unseen Outer period.

## Bounded method

- Candidate sets: Schema 3.0 Baseline or Baseline plus `session_progress`.
- Fixed model: raw depth-5 balanced random forest.
- Fixed policy: argmax.
- Four Outer folds, three Inner folds, and 16-record purges.
- Timestamp-only derivation; no future rows are used.
- Validation and Test are never read.

## Focused validation

`training/test_nested_session_context_diagnostic.py` verifies the exact two-set boundary and established weakest-gate selection rule. It passed with the Session encoding and nested purge tests.

## Inner selection result

| Outer history | Baseline gate floor | Session Progress gate floor | Selected |
| --- | ---: | ---: | --- |
| 1 | 0.7867 | 0.8256 | Session Progress |
| 2 | 0.7949 | 0.8113 | Session Progress |
| 3 | 0.9060 | 0.8894 | Baseline |
| 4 | 0.9153 | 0.9393 | Session Progress |

Session Progress was selected before `3/4` Outer periods. Full-Train Inner selection also preferred Session Progress, though only narrowly on the weakest-gate ratio.

## Outer estimate

- Accuracy: `0.4142`.
- Macro F1: `0.3976`.
- SELL precision/recall: `0.5373 / 0.4078`.
- BUY precision/recall: `0.4174 / 0.3754`.
- Complete passing Outer folds: `0/4`.

Compared with the fixed Baseline Outer estimate (`0.4107` Accuracy, `0.3939` Macro F1, `0.4066` BUY precision, `0.3721` BUY recall), the nested selection improved all four listed aggregate measurements while slightly reducing SELL precision from `0.5425`.

## Decision

This is the first proposed context extension selected consistently in a majority of Inner histories and improving the mixed unseen Outer estimate. It justifies formal architecture and interface review for one Session-group field.

It does not pass the deployment gate, does not authorize an MQL5 change by itself, and does not authorize Validation/Test reuse. CR-001 defines the proposed implementation boundary and required approval.

