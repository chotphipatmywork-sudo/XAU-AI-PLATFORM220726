# IMP-032 Purged Temporal Evaluation

Status: Implemented and locally compiled; regenerated-partition runtime validation pending.

## Purpose

Label Schema 1.1 determines each class from the following 16 M15 bars. A merely chronological split can therefore leak evaluation-period prices through the labels of records immediately before a boundary. This implementation removes that overlap without changing the approved labels, features, Brain replay, runtime flow, or raw dataset.

## Approved method

- `CDatasetSplitter` purges 16 source records before Validation and 16 before Test.
- The split report reconciles Train, Validation, Test, and 32 purged records to the raw total.
- `CDatasetPartitionValidator` requires boundary timestamp gaps compatible with the purge.
- `walk_forward_select.py` purges 16 records before every internal evaluation fold.
- `ChronologicalCalibratedClassifier` purges 16 records between base-estimator fitting and probability calibration.
- The Train-only walk-forward feature diagnostic reads and applies the purge value recorded by the selection report.

The purge is fixed at 16 for Feature Schema 3.0 and Label Schema 1.1. Changing it requires label calibration and schema review.

## Boundary

This is an offline evaluation correction only. It does not change `Market -> Brain -> AI Runtime -> Decision -> Risk -> Execution -> Trade Lifecycle`, authorize deployment, or place orders. The raw `XAU_AI_TRAINING_DATASET.csv` does not need regeneration; only its three partition files and downstream Python artifacts must be recreated.

## Validation order

1. Compile and run `tests/TestDatasetSplitter.mq5`.
2. Compile and run `tests/TestDatasetPartitionValidator.mq5`.
3. Run `tests/TestDatasetReadinessGate.mq5`.
4. Run `training/test_walk_forward_training.py` and the other focused Python tests.
5. Rerun Train-only walk-forward selection and its feature diagnostic.

All pre-purge model metrics are historical diagnostics and are not deployment evidence.

## Local validation

MetaEditor compilation passed with 0 errors and 0 warnings for `TestDatasetSplitter.mq5`, `TestDatasetPartitionValidator.mq5`, and `TestDatasetReadinessGate.mq5`. Python syntax checks plus `test_walk_forward_training.py`, `test_walk_forward_feature_diagnostic.py`, and `test_probability_decision_policy.py` passed. Runtime regeneration remains in the MT5 data-folder copy.
