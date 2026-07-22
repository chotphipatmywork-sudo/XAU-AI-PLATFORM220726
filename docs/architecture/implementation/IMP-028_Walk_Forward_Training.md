# IMP-028 Walk-Forward Training and Calibration

Status: Purged walk-forward methodology implemented; post-purge evaluation pending.

## Purpose

Repeated Train/Validation candidate experiments did not pass the Model Evaluation Contract and risk adapting development choices to one Validation period. This implementation moves candidate and policy selection inside Train using expanding chronological folds. It does not read the existing Validation or Test partitions.

## Temporal method

`training/walk_forward_select.py` reserves the first 50% of Train as the initial history and evaluates four consecutive forward blocks. Each fold excludes the 16 records immediately before its evaluation block, matching the Label Schema 1.1 horizon. Later folds expand the training history while preserving the same purge.

Every model is evaluated with raw probabilities and with chronological calibration. The calibrated variant trains its base estimator on the early portion of each fold's training history, purges 16 records, then fits a multinomial probability calibrator on the following 20%. Neither the estimator labels nor calibration labels can observe prices in the next stage.

Candidate ranking prioritizes a stable gate across all folds, then the number of folds passing the gate, aggregate macro F1, and aggregate accuracy. Probability policies remain offline selection metadata and do not alter AI Runtime, Decision, Risk, Execution, or Trade Lifecycle.

## Artifacts and boundary

The script writes a locked joblib candidate, its paired policy JSON, and full walk-forward diagnostics. These are development artifacts only. They are not ONNX artifacts, are not loadable by MQL5, and do not authorize trading. A newly generated later-period evaluation set is required after the methodology is frozen.

## Focused validation

Run `training/test_walk_forward_training.py`. It verifies the 16-record gap at every expanding-fold and internal calibration boundary, then checks that the chronological calibrator returns valid three-class probabilities without reading any project dataset.

## Methodology correction

The earlier results below were produced before label-horizon purging was enforced. They remain useful development history but are not valid evidence for deployment or final model comparison. After `TestDatasetSplitter.mq5` recreates purged partitions, walk-forward selection and the Train-only feature diagnostic must be rerun before further model decisions.

The purged rerun selected `random_forest_depth_10_balanced` with raw argmax and produced Accuracy `0.4528`, Macro F1 `0.4227`, and BUY precision `0.4133`. Because these same folds also selected the candidate, IMP-033 introduced a nested purged estimate. The nested Outer result fell to Accuracy `0.4236`, Macro F1 `0.3839`, and BUY precision `0.3711`, confirming that this non-nested result must not be treated as deployment evidence.

## Evaluation result

The focused test passed. User-environment execution evaluated 2,338 forward records over four expanding folds without reading Validation or Test. The selected development candidate was `random_forest_depth_10_hold_2` with raw probabilities and argmax.

| Metric | Aggregate result | Required |
| --- | ---: | ---: |
| Accuracy | 0.4555 | 0.45 |
| Macro F1 | 0.4018 | 0.40 |
| SELL precision | 0.5258 | 0.50 |
| SELL recall | 0.5571 | 0.30 |
| BUY precision | 0.4178 | 0.50 |
| BUY recall | 0.3628 | 0.30 |

No candidate passed the aggregate gate and zero of four folds passed the complete gate. Raw probabilities outperformed chronological calibration for the selected candidate. The repeated BUY-precision failure across ordinary Validation and internal walk-forward evaluation indicates a directional-separability limitation in the current four-scalar representation, not merely a threshold or probability-calibration issue. The locked artifact remains a development artifact and is not eligible for deployment.

## Feature Contract 2.0 result

After approved Feature Contract 2.0 dataset regeneration, Train contained 4,672 records. The selected Train-only candidate changed to `random_forest_depth_10_balanced` with raw probabilities and argmax. Aggregate Macro F1 improved to `0.4140`, BUY recall improved to `0.4225`, and HOLD recall improved to `0.4387`; however BUY precision remained `0.4192`. No candidate passed the aggregate gate and zero of four folds passed the complete gate. Validation and Test remained unread. IMP-030 therefore adds a Train-only fold-level feature diagnostic before any further feature-contract proposal.
