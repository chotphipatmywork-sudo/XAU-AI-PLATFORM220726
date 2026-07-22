# IMP-029 Feature Contract 2.0

Historical status: implemented and evaluated; superseded by approved Feature Contract 3.0.0 in IMP-031.

## Decision

Feature Contract 2.0 preserves the canonical Trend, Volatility, Liquidity, and Session groups while expanding the model tensor from four scalars to eight dimensions:

1. `trend_regime`
2. `trend_momentum`
3. `trend_slope`
4. `volatility`
5. `liquidity`
6. `session_asia`
7. `session_london`
8. `session_new_york`

The three Trend values are the existing Schema 1.4 ATR-normalized components before their weighted scalar collapse. The three Session values use strict one-hot encoding. Features remain generated only from replayed Brain output.

## Rationale

The Schema 1.4 Train-only walk-forward experiment met aggregate accuracy and macro-F1 thresholds but failed BUY precision in every fold. Diagnostics indicated that collapsing distinct Trend horizons and treating Session as an ordinal scalar limited directional separability. This change preserves the approved feature groups while allowing the model to learn their internal relationships.

## Boundaries

- `Trend.Strength` and the Decision Runtime are unchanged.
- Historical Label Schema 1.1.0 remains M15, 16 bars, and +/-1.5 ATR(14).
- Confidence, Risk, execution results, and trade outcomes remain excluded.
- Live inference remains independent from offline training and dataset generation.
- No model produced under Feature Schema 1.x is compatible with this contract.

## Validation

Compile `tests/TestAITrendScore.mq5`, `tests/TestBrainFeatureAdapter.mq5`, `tests/TestModelTrainingContract.mq5`, and `tests/TestHistoricalDatasetOrchestrator.mq5`. After copying the updated source to MT5, regenerate the dataset with replace enabled, then run Dataset Validator, Splitter, Partition Validator, and Readiness Gate before any Python selection experiment.
