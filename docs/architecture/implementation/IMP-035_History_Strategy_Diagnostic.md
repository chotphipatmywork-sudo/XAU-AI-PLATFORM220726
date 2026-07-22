# IMP-035 Purged History Strategy Diagnostic

Status: Implemented and evaluated; expanding history retained.

## Purpose

IMP-034 found temporal shift concentrated in Trend features. `training/history_strategy_diagnostic.py` tests whether old regimes are degrading performance by changing only the training-history strategy while holding the model, probability variant, policy, folds, labels, and feature contract constant.

## Controlled method

- Model: `random_forest_depth_5_balanced`
- Probability: raw
- Decision policy: argmax
- Evaluation: the same four Train-only Outer periods
- Boundary purge: 16 records
- Strategies: expanding; rolling 1,000/1,500/2,000 records; exponential recency half-life 500/1,000/2,000 records

Recency weights have mean one and increase exponentially toward the newest sample. Rolling windows retain only the newest configured records. No strategy changes chronological order, reads Validation/Test, or writes a deployable artifact.

## Focused validation

`training/test_history_strategy_diagnostic.py` verifies active contract-version metadata, newest-record rolling selection, increasing normalized recency weights, and the fixed seven-strategy grid. This prevents active Schema 4.0 evidence from being emitted with a stale Schema 3.0 identifier.

## Result

| Strategy | Accuracy | Macro F1 | BUY precision | BUY recall |
| --- | ---: | ---: | ---: | ---: |
| Expanding | 0.4107 | 0.3939 | 0.4066 | 0.3721 |
| Recency half-life 2000 | 0.4103 | 0.3926 | 0.3966 | 0.3620 |
| Recency half-life 1000 | 0.4077 | 0.3889 | 0.3867 | 0.3698 |
| Rolling 2000 | 0.4047 | 0.3817 | 0.3838 | 0.3486 |
| Recency half-life 500 | 0.4000 | 0.3808 | 0.3767 | 0.3911 |
| Rolling 1000 | 0.4069 | 0.3792 | 0.3593 | 0.3397 |
| Rolling 1500 | 0.3948 | 0.3690 | 0.3555 | 0.3352 |

No strategy passed any complete fold gate. Expanding history ranked first on the weakest-gate criterion and produced the best aggregate Macro F1 and BUY precision. Recency half-life 1,000 improved Fold 4 Macro F1 from `0.3622` to `0.3803`, but reduced Fold 1 Macro F1 from `0.3636` to `0.3242`. Rolling 2,000 improved some middle folds but degraded the first and last folds.

## Decision

Static rolling windows and static recency weighting are rejected as the next model method. Older data are not the primary aggregate failure, and expanding history remains the baseline. Because different history strategies help different periods, the next investigation should measure whether the relationship between approved feature regimes and future labels changes across time. This must remain a Train-only diagnostic before proposing any feature or model-contract change.

## Expanded-history result

The controlled comparison was repeated on the 18,788-record expanded Train partition under active contracts `4.0.0/4.0.0/1.1.0`. Validation and Test were not read.

Rolling 1,000 records ranked first with Accuracy `0.4367`, Macro F1 `0.4158`, SELL precision `0.4711`, and BUY precision `0.4847`. It passed no complete fold. The next-ranked recency half-life 500 strategy produced Macro F1 `0.4111`, SELL precision `0.4708`, and BUY precision `0.4853`, also with zero passing folds.

The wider history changes the diagnostic ranking from expanding to rolling 1,000, but it does not establish a stable history method. All seven strategies passed `0/4` complete gates, and neither directional precision threshold reached `0.50` for the best strategy. Rolling 1,000 therefore remains a research hypothesis only and cannot replace the registered expanding method or authorize deployment.
