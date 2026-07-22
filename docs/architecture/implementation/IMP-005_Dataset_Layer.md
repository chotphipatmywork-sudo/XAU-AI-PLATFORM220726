# IMP-005 Dataset Layer

Status: Implemented for Phase 6 foundation.

## Scope

The Dataset Layer persists normalized AI training samples independently from live inference. Feature Schema 3.0.0 contains eleven model dimensions within the same four canonical groups: three Trend components, two Volatility components, three Liquidity components, and three one-hot Session fields. Its target label is stored separately.

## Components

- `CAITrainingSample` owns features and label.
- `CDatasetRecord` owns sample metadata.
- `CDatasetWriter` appends CSV records in the MQL5 file sandbox and supports explicit batch flushing.
- `CDatasetReader` reads those records for offline training.
- `CDatasetManager` coordinates access modes.

## Boundary

This implementation does not change the live runtime path or the Risk and Execution boundaries. `CAITrainingEngine` is the only current consumer.

## Validation

`tests/TestDataset.mq5` provides a smoke-test entry point. Local MetaEditor compilation passed with 0 errors and 0 warnings for Feature Schema 3.0.0.

Historical generation flushes completed batches at its configured progress interval rather than forcing a disk flush for every CSV row. This preserves explicit checkpoints while avoiding per-record filesystem overhead.
