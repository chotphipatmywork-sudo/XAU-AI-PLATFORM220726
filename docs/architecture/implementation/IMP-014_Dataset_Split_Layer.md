# IMP-014 Dataset Split Layer

Status: Purged temporal split implemented and compiled; runtime partition regeneration pending.

## Purpose

`CDatasetSplitter` creates separate offline Train, Validation, and Test CSV files from one validated historical dataset.

## Anti-leakage rule

The splitter never shuffles records. It requires strictly increasing timestamps, then assigns the oldest records to Train, the next records to Validation, and the newest records to Test. Because Label Schema 1.1 uses the following 16 M15 bars, the last 16 records before both the Validation and Test boundaries are excluded from every output partition. This prevents labels in an earlier partition from observing prices inside the following evaluation partition.

## Default partition

- Train: 70%
- Validation: 15%
- Test: 15%

Rounding is first applied to the original 70% and 15% boundaries. Sixteen records are then purged from the end of the Train allocation and another sixteen from the end of the Validation allocation. All remaining newest records go to Test. Each written partition must contain at least one record, and the split report must reconcile written plus purged records to the raw total.

For a raw dataset of 6,679 records, the expected output is Train `4,659`, Validation `985`, Test `1,003`, and Purged `32`.

## Files

The focused EA `tests/TestDatasetSplitter.mq5` reads `XAU_AI_TRAINING_DATASET.csv` and replaces these output files in the MQL5 Files sandbox:

- `XAU_AI_TRAINING_TRAIN.csv`
- `XAU_AI_TRAINING_VALIDATION.csv`
- `XAU_AI_TRAINING_TEST.csv`

The input file is never changed. Output names must differ from each other and from the input file.

Focused MetaEditor compilation of `tests/TestDatasetSplitter.mq5` passed with 0 errors and 0 warnings.
