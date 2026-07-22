# IMP-046 One-shot Historical Dataset Orchestrator Test

Status: Implemented; local MetaEditor validation passed; MT5 copy/runtime confirmation pending.

## Problem

The Schema 4.0 dataset generation completed with 6,679 records at `2026.07.15 16:17:10.697`, but `TestHistoricalDatasetOrchestrator` remained attached to the chart. A later terminal/chart reinitialization started the destructive replace-mode test again at `21:07:41.879`.

The user attached `TestDatasetValidator` while the second generation was processing. MT5 terminated the Orchestrator at `21:08:05.015`, after it had written only 2,709 rows. The partial file remained structurally valid but no longer covered the complete history.

## Change

`TestHistoricalDatasetOrchestrator.mq5` now calls `ExpertRemove()` after printing the final record count. MT5 unloads the test after the current initialization event returns, preventing an already completed destructive test from restarting automatically after terminal or chart reinitialization.

The production Orchestrator class, Feature Contract, Label Contract, and runtime architecture are unchanged.

## Validation

Local MetaEditor compilation of the updated focused test passed with `0 errors / 0 warnings` in 2,970 ms. Runtime confirmation requires one complete replace-mode generation followed by verification that the test is no longer shown as the active chart Expert.

## Recovery

The partial 2,709-row file must not be split or trained. Copy and compile the updated one-shot test in MT5, regenerate with replace mode, and rerun Dataset Validator only after the final complete record count is printed.
