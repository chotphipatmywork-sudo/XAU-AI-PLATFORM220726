# IMP-057 Past Price Action Context Research

Status: Evaluated; proposal rejected before nested confirmation.

## Purpose

Test whether bounded completed-bar price displacement and range context add
information that the EMA/ATR/volume-based Schema 4.0 snapshot does not contain.

## Fixed timing

For Dataset bar `t`, the observation time is the close of `t`.

- current candle OHLC at `t` is complete;
- returns use closes at `t-1`, `t-4`, and `t-16`;
- prior range uses only bars `t-1` through `t-16`;
- ATR(14) is read at `t`;
- label evaluation begins at `t+1`.

No forming or future bar is permitted.

## Fixed encodings

- signed ATR encoding: `50 + 25 * value / ATR`, clamped to `0..100`;
- positive ATR encoding: `50 * value / ATR`, clamped to `0..100`;
- range/candle position: percentage from low to high, clamped to `0..100`.

Rows that cannot be calculated must contain eight neutral `50` values and
`price_action_valid=0`. The validity flag is join/coverage metadata and is not
a candidate model input.

## Fixed validation

- focused MetaEditor synthetic encoding and closed-bar timing test;
- exact Dataset ID/Timestamp join;
- no duplicate keys;
- bounded/neutral-invalid validation;
- four controlled Train-only folds with purge 16;
- conditional nested confirmation only after controlled promotion;
- Validation/Test remain unread.

## Protected boundary

The exporter is research-only. It does not modify `CTrendAnalyzer`,
`CVolatilityAnalyzer`, `CLiquidityAnalyzer`, `CBrainFeatureAdapter`, Dataset
Writer, AI Runtime, Decision, Risk, Execution, or Trade Lifecycle.

## Implemented files

- `core/ai/HistoricalPriceActionContextExporter.mqh`
- `tests/TestHistoricalPriceActionContextExporter.mq5`
- `tools/sync_price_action_research_to_mt5.ps1`
- `training/price_action_context_diagnostic.py`
- `training/test_price_action_context_diagnostic.py`
- `training/nested_price_action_context_diagnostic.py`
- `training/test_nested_price_action_context_diagnostic.py`

The nested script is registered before controlled evidence and refuses to run
unless the controlled report authorizes exactly one non-Baseline feature set.

## Python validation

Focused join, coverage, candidate-grid, promotion-boundary, and conditional
nested tests passed. Full training regression:

`PYTHON TESTS PASSED: 27/27`

## Compile evidence

MetaEditor compile of
`tests/TestHistoricalPriceActionContextExporter.mq5`:

`Result: 0 errors, 0 warnings, 1091 ms elapsed, cpu='X64 Regular'`

Workspace and MT5 source hashes match. Compile log:
`training/output/expanded_20260716/compile_price_action.log`

## Evidence result

- auxiliary records: `26,864`
- exact Dataset-key join: true
- duplicate/invalid records: `0/0`
- valid coverage: `100%`
- Validation/Test read: false/false

All Price Action ranked first with gate floor `0.9207`, compared with Baseline
`0.9131`, but the improvement `0.0076` did not reach the registered `0.01`
minimum. Completed Candle Impulse raised Macro F1 from `0.3948` to `0.3973`.
Every feature set passed `0/4` complete folds.

No candidate was promoted and nested confirmation remained unauthorized.
Runtime, Feature Schema 4.0, Validation, Test, and deployment are unchanged.
