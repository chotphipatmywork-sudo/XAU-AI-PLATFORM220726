# IMP-010 Historical Dataset Orchestration

Status: Implemented; pending MetaEditor compilation validation.

## Large dataset handling

Historical Brain results are replayed and persisted one bar at a time. The orchestrator does not allocate a full `CBrainAnalysisResult` array for the requested history range. This keeps memory use bounded when generating multi-thousand-bar datasets.

The focused test exposes `ProgressInterval` (default: 100) and writes progress to the Experts log. Production callers leave the optional interval at `0` to remain silent.
Each progress checkpoint flushes the completed CSV batch to disk.

`CHistoricalDatasetOrchestrator` coordinates the offline-only path:

`Historical Data Provider -> Historical Brain Replay -> Historical Dataset Builder -> Dataset CSV`

Before any sample is written, it requires the loaded M15 rates and ATR arrays to have equal lengths. For each rate it resolves the exact MQL5 bar shift, then replays Brain analysis at that shift. This prevents the replay from accidentally evaluating the current bar instead of the historical feature bar.

The orchestrator has no live tick, inference, Risk, Execution, or Trade Lifecycle dependency. `tests/TestHistoricalDatasetOrchestrator.mq5` is the focused compile and smoke-test entry point.
