# IMP-026 Multi-Horizon AI Trend Score

Historical status: Feature Schema 1.4.0 is superseded by approved Feature Contract 2.0.0 in IMP-029.

Status: Implemented; pending MetaEditor compilation validation.

## Decision

Feature Schema 1.4.0 retains the canonical four-feature AI input while replacing only the internal calculation of the existing Trend feature. It is based on the Schema 1.3.0 Train/Validation-only diagnostic: Trend had a small Validation permutation macro-F1 drop of `0.0090`, while the Test partition remained unread.

## Calculation

`CTrendAnalyzer` reads the current EMA 50, EMA 200, ATR(14), current EMA 50 slope, and EMA 50 at a completed 16-bar lookback. `CTrendAssembler` turns these three ATR-normalized signed signals into one score:

- EMA 50/200 regime: 45%.
- EMA 50 movement over 16 completed bars: 40%.
- Current EMA 50 slope: 15%.

Each component is capped in the range -1..1. A valid CHOCH halves the combined value. The final `AITrendScore` is mapped around neutral 50 and clamped to 0..100.

The 16-bar input is historical information available at the analyzed bar; it does not read the future label horizon. `Trend.Strength`, `Trend.Direction`, and `Trend.Confidence` remain unchanged, so the Decision Runtime behavior is unchanged.

## Compatibility

All Schema 1.3.0 CSV partitions and preliminary model artifacts are incompatible with Schema 1.4.0. Regenerate the dataset, validate and split it, then use Train and Validation only for candidate selection. Do not use Test until a candidate passes the Validation gate.

## Focused validation

Compile `tests/TestAITrendScore.mq5`, `tests/TestBrainFeatureAdapter.mq5`, and `tests/TestModelTrainingContract.mq5` in MetaEditor. The historical dataset orchestrator must report Feature Schema `1.4.0` before generating new CSV partitions.
