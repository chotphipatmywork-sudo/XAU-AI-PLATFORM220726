# AI Model Evaluation Contract

Status: Phase 7 baseline.

## Scope

This contract defines the minimum offline metrics a trained three-class model must report on both time-ordered Validation and Test datasets. It is framework-independent and does not perform training, inference, or trading.

## Required metrics

Every metric is a ratio in 0..1. The trainer must provide:

- sample count
- accuracy
- macro F1 across SELL, HOLD, BUY
- BUY precision and recall
- SELL precision and recall

Macro F1 is required because HOLD is uncommon in the current dataset; accuracy alone could hide poor minority-class performance.

## Baseline thresholds

| Metric | Minimum |
|---|---:|
| Samples in each Validation/Test evaluation | 100 |
| Accuracy | 0.45 |
| Macro F1 | 0.40 |
| BUY precision | 0.50 |
| SELL precision | 0.50 |
| BUY recall | 0.30 |
| SELL recall | 0.30 |

Both Validation and Test metrics must meet every threshold.

## Meaning of a pass

Passing grants only `EligibleForShadowDeployment=true`: the model may advance to a non-trading technical integration or shadow-evaluation stage. It does not authorize live orders, bypass AI Decision, bypass Risk, or approve production deployment. Thresholds are baseline quality gates and require future walk-forward calibration.
