# IMP-016 Dataset Training Readiness

Status: Implemented; pending MetaEditor compilation validation.

## Purpose

Dataset validity and model-training readiness are different. `CDatasetReadinessGate` consumes the read-only partition validation result and applies explicit minimum-size and label-coverage thresholds before a dataset is considered ready for external model training.

## Default thresholds

- Total records: at least 1,000
- Train / Validation / Test records: at least 700 / 100 / 100
- Each BUY, HOLD, and SELL class in every partition: at least 5 records

These are minimum safety thresholds, not a claim that the dataset will produce a profitable model. They are inputs in `TestDatasetReadinessGate.mq5` and may be tightened later based on the selected training algorithm and walk-forward evaluation plan.

## Behaviour

The gate does not write, delete, or modify any CSV. It reports `Ready=false` for a structurally valid but undersized or label-incomplete dataset. This protects the future training path while leaving the live inference runtime independent.
