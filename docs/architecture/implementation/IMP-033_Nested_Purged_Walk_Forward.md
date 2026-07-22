# IMP-033 Nested Purged Walk-Forward Selection

Status: Implemented and evaluated; no candidate passed the nested outer gate.

## Purpose

The ordinary purged walk-forward experiment used the same forward folds to select a candidate and report its score. That score is useful for development ranking but can be optimistic. `training/nested_walk_forward_select.py` separates those responsibilities while remaining entirely inside the purged Train partition.

## Method

- Four Outer folds estimate the complete selection process.
- Three Inner folds select the model, raw or calibrated probability variant, and decision policy separately inside each Outer history.
- Every Inner, Outer, and calibration boundary purges the approved Label Schema 1.1 horizon of 16 M15 records.
- The policy grid tests independent SELL and BUY confidence floors plus directional margins.
- Ranking first considers stable contract passage, passed folds, aggregate passage, and the weakest metric relative to its contract threshold; Macro F1 and accuracy break later ties.
- Validation and Test are never read.

After Outer evaluation, a final development configuration is selected with Inner folds over the complete Train partition and fitted only to Train. Its joblib and policy JSON remain Python-only development artifacts with `deployment_authorized=false`.

## Focused validation

`training/test_nested_walk_forward_training.py` verifies the 16-record Inner and Outer purge, the asymmetric policy grid, confidence behavior, and weakest-gate ranking. It passed together with the existing purged walk-forward and probability-policy tests.

## Train-only result

The user-environment evaluation used 4,659 purged Train records, four Outer folds, and three Inner folds. It read neither Validation nor Test.

| Metric | Nested Outer result | Required |
| --- | ---: | ---: |
| Accuracy | 0.4236 | 0.45 |
| Macro F1 | 0.3839 | 0.40 |
| SELL precision | 0.5033 | 0.50 |
| SELL recall | 0.5186 | 0.30 |
| BUY precision | 0.3711 | 0.50 |
| BUY recall | 0.3184 | 0.30 |

No Outer fold passed the complete evaluation gate. Inner selections changed between calibrated confidence policies and raw argmax, and one calibrated Outer evaluation collapsed to SELL-only predictions. This demonstrates temporal instability and confirms that the earlier non-nested score was optimistic.

The full-Train Inner selection chose `random_forest_depth_5_balanced`, raw probabilities, SELL minimum `0.35`, BUY minimum `0.40`, and zero margin. Its Inner Macro F1 was `0.3814` and BUY precision was `0.4335`; it is not eligible for deployment.

## Decision

Do not open Validation or Test and do not deploy the locked artifact. The next investigation must target temporal generalization inside the approved Trend, Volatility, Liquidity, and Session groups. Probability threshold tuning alone is rejected as the solution because it did not remain stable on unseen Outer periods.

## Feature Schema 4.0 reevaluation

The regenerated Schema 4.0 Train partition contained 4,656 records after the approved external boundary purge. The same nested method was rerun with strict Schema 4.0 input and read neither Validation nor Test.

| Metric | Nested Outer result | Required |
| --- | ---: | ---: |
| Accuracy | 0.4175 | 0.45 |
| Macro F1 | 0.3405 | 0.40 |
| SELL precision | 0.4993 | 0.50 |
| SELL recall | 0.6526 | 0.30 |
| BUY precision | 0.3636 | 0.50 |
| BUY recall | 0.1171 | 0.30 |

No Outer fold passed the complete gate. The complete-Train Inner selection chose `random_forest_depth_8_hold_4`, raw probabilities, SELL minimum `0.35`, BUY minimum `0.40`, and zero margin; that configuration also failed its Inner aggregate gate. The locked artifact remains non-deployable and its policy metadata retains `deployment_authorized=false`.
