# IMP-015 Dataset Partition Validation

Status: Purge-boundary validation implemented and compiled; regenerated-partition runtime validation pending.

`CDatasetPartitionValidator` validates the Train, Validation, and Test CSV files as one offline dataset set. It checks that every file is readable and non-empty, each file is strictly timestamp-ordered, record IDs and timestamps are unique across all three files, feature values are within 0..100, and labels are BUY/HOLD/SELL only.

The validator also verifies the temporal boundary rule and the minimum M15 gap created by the approved 16-record purge:

`last(Train) < first(Validation) < last(Validation) < first(Test)`

Each boundary must span at least 17 M15 timestamp intervals from the last retained earlier record to the first later record. A larger timestamp gap is accepted because market closures and missing broker bars can lengthen elapsed time. The splitter's reconciled purge count remains the primary proof that exactly 16 source records were omitted per boundary.

It prints the record count and BUY/HOLD/SELL distribution of each partition. It never changes the dataset files.

Run `tests/TestDatasetPartitionValidator.mq5` after `TestDatasetSplitter.mq5` and before exporting the data to a model-training environment.

Focused MetaEditor compilation of `tests/TestDatasetPartitionValidator.mq5` and the dependent `tests/TestDatasetReadinessGate.mq5` passed with 0 errors and 0 warnings.
