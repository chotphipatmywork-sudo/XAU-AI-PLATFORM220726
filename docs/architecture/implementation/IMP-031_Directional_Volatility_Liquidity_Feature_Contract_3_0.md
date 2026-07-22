# IMP-031 Directional Volatility and Liquidity Feature Contract 3.0

Status: Approved and implemented; local MQL5 and Python validation passed, regenerated-dataset validation pending.

## Decision

Feature Contract 3.0 preserves the canonical Trend, Volatility, Liquidity, and Session groups while expanding the model tensor from eight to eleven dimensions:

1. `trend_regime`
2. `trend_momentum`
3. `trend_slope`
4. `volatility_regime`
5. `volatility_change`
6. `liquidity_activity`
7. `liquidity_range_position`
8. `liquidity_sweep_direction`
9. `session_asia`
10. `session_london`
11. `session_new_york`

## Rationale

The Feature Contract 2.0 Train-only walk-forward diagnostic found that existing scalar Liquidity and Volatility values contributed positively to Macro F1 in all folds but provided weak and inconsistent BUY-precision information. Trend regime and medium momentum remained the strongest BUY-precision contributors. Schema 3.0 therefore exposes the temporal Volatility regime and directional Liquidity context already produced by the canonical Brain path instead of changing labels or adding a new feature group.

## Encoding

- `volatility_regime` maps current ATR relative to the preceding 16 ATR values around neutral 50.
- `volatility_change` retains the existing short ATR-change projection used by Feature Contract 2.0.
- `liquidity_activity` retains the existing Liquidity score.
- `liquidity_range_position` maps the current close from reference low `0` to reference high `100` over the preceding 10 bars.
- `liquidity_sweep_direction` maps a buy-side/high sweep to `0`, no or double sweep to `50`, and a sell-side/low sweep to `100`.
- Session remains a strict three-column one-hot group.

## Runtime preservation

Runtime Volatility confidence and Liquidity score are unchanged. The placeholder inference path continues to reconstruct its legacy four-group score from Trend, `volatility_change`, `liquidity_activity`, and Session. Decision, Risk, Execution, Trade Lifecycle, and Label Schema 1.1.0 remain unchanged.

## Compatibility and validation

All Feature Schema 2.0 CSV files and model artifacts are incompatible. Regenerate the full historical dataset with replace enabled, then run Dataset Validator, Splitter, Partition Validator, and Readiness Gate before any Train-only model experiment.

Focused local MetaEditor compilation passed with 0 errors and 0 warnings for Liquidity, Volatility, Brain adapter, model contract, historical orchestration, dataset validation, historical replay, and the complete compile smoke test. Python syntax and the probability-policy, walk-forward, and walk-forward feature-diagnostic tests also passed.
