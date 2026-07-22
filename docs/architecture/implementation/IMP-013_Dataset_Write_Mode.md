# IMP-013: Dataset Write Mode

## Purpose

Historical dataset generation must create a clean, reproducible training file by default.

## Behaviour

- `CHistoricalDatasetOrchestrator::Build()` replaces `XAU_AI_TRAINING_DATASET.csv` unless explicitly told to append.
- The focused EA test exposes `ReplaceExistingDataset=true` as its default input.
- Replacing deletes the previous CSV before writing the header and new records.
- Appending is opt-in. When it is selected, `CDatasetManager` continues record IDs after the largest existing ID.
- Direct users of `CAITrainingEngine::Initialize()` keep the existing append-by-default behaviour; the replacement policy is limited to historical dataset generation.

## Safety

`ReplaceExistingDataset=true` permanently replaces the prior dataset file. Copy or rename a dataset first when it must be retained.

## Validation

After one replacement-generation run, `TestDatasetValidator.mq5` should report zero duplicate IDs and zero duplicate timestamps. The exact record total may be lower than the requested bar count because bars without enough historical context or future label horizon are skipped.
