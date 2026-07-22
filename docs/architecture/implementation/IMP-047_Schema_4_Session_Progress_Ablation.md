# IMP-047 Schema 4.0 Session Progress Ablation

Status: Implemented and evaluated; Session Progress retained, deployment gate closed.

## Purpose

Feature Schema 4.0 has been regenerated and passed Dataset, Partition, temporal-purge, and Readiness validation. The ordinary Train-only walk-forward method did not pass the stable model gate. Its grouped permutation report showed that Session context contributed to Macro F1 in all four folds, but it could not isolate the new `session_progress` field from the three Session one-hot fields.

`training/schema4_session_progress_ablation.py` performs that bounded comparison without changing Runtime or the active Feature Contract.

## Controlled boundary

The diagnostic reads only the strict Schema 4.0 Train partition and compares:

1. the first eleven fields, excluding only final `session_progress`;
2. all twelve Schema 4.0 fields.

Both candidates use the same `random_forest_depth_10_hold_2` model, raw probabilities, argmax policy, four Outer folds, three Inner folds, and a 16-record purge. Inner folds select the feature set before each unseen Outer period using the established stable-gate and weakest-gate ordering.

Validation and Test are not accepted as inputs. The output is diagnostic evidence only and cannot authorize deployment.

## Validation

`training/test_schema4_session_progress_ablation.py` verifies the exact two-set boundary, removal of only the final Session Progress field, preservation of the complete tensor, and weakest-gate selection behavior.

## Next decision

The focused test passed. The nested ablation selected `with_session_progress` before three of four Outer periods and from the complete Train history. Aggregate Outer Accuracy was `0.4472`, Macro F1 `0.4143`, SELL precision `0.5043`, BUY precision `0.3870`, and BUY recall `0.3362`. No Outer fold passed the complete gate.

Keep Feature Schema 4.0 unchanged because the past-only selection repeatedly retained Session Progress. The field is not sufficient to authorize deployment: the complete model-selection method must still undergo nested Train-only evaluation and later untouched-period evaluation under the approved contract.
