# IMP-012 Dataset Validation

Status: Implemented; pending MetaEditor compilation validation.

`CDatasetValidator` opens a dataset CSV in read-only mode. It reports total records, BUY/HOLD/SELL labels, duplicate record IDs, duplicate timestamps, invalid feature ranges, and invalid labels.

A dataset is valid only when it contains at least one record and no validation errors. The validator does not modify the dataset file.

`tests/TestDatasetValidator.mq5` is an EA-style test that prints the report to the MetaTrader Experts log.
