# IMP-058 16-Bar Price Path State Research

Status: Controlled evidence complete; rejected.

## Fixed timing and input

At the close of Dataset bar `t`, load:

- closes from `t` through `t-16`;
- highs/lows from `t` through `t-15`;
- ATR(14) at `t`.

Every value is known at the feature observation time. Label evaluation starts
at `t+1`.

## Fixed calculations

- directional efficiency:
  `(close[t] - close[t-16]) / sum(abs(close[i] - close[i-1]))`
- up-close ratio: positive changes / non-flat changes
- run balance: `(longest_up_run - longest_down_run) / 16`
- sign persistence: `(same_adjacent_signs - opposite_adjacent_signs) / valid_pairs`
- path travel ATR encoding: `50 * travel / (8 * ATR)`, clamped
- range efficiency: `100 * 16_bar_range / travel`, clamped
- range expansion: `50 * recent_8_range / earlier_8_range`, clamped

Unavailable rows must contain seven neutral `50` values and
`price_path_valid=0`. The validity flag is metadata only.

## Protected boundary

Research code must not modify Brain analyzers, canonical features, Dataset
generation, AI Runtime, Decision, Risk, Execution, or Trade Lifecycle.

## Required validation

- one class per `.mqh`;
- synthetic engine test;
- closed-bar timing test;
- MetaEditor compile with zero errors/warnings;
- exact Dataset-key join and bounded coverage;
- fixed Train-only controlled comparison;
- conditional nested confirmation only after promotion.

## Implemented files

- `core/brain/trend/models/PricePathStateResult.mqh`
- `core/brain/trend/engines/PricePathStateEngine.mqh`
- `core/ai/HistoricalPricePathStateExporter.mqh`
- `tests/TestHistoricalPricePathStateExporter.mq5`
- `tools/sync_price_path_research_to_mt5.ps1`
- `training/price_path_state_diagnostic.py`
- `training/test_price_path_state_diagnostic.py`
- `training/nested_price_path_state_diagnostic.py`
- `training/test_nested_price_path_state_diagnostic.py`

## Pre-export validation

- focused controlled diagnostic test: passed
- focused conditional nested diagnostic test: passed
- complete Python regression: 29/29 passed
- workspace/MT5 SHA-256 verification: all four MQL5 research files match
- MetaEditor focused exporter compile and run: operator-confirmed
- auxiliary export: 26,864 records written

## Controlled evidence

- exact Dataset-key coverage: 26,864/26,864
- valid auxiliary rows: 26,864
- duplicate or missing joined keys: 0
- Validation dataset used: false
- Test dataset used: false
- future rows used: false

The fixed ranking was:

1. `schema4_baseline`: Macro F1 `0.394773`, gate floor `0.913112`, `0/4` folds
2. `trend_path_state`: Macro F1 `0.393123`, gate floor `0.911693`, `0/4` folds
3. `volatility_path_state`: Macro F1 `0.390513`, gate floor `0.902467`, `0/4` folds
4. `all_price_path_state`: Macro F1 `0.388547`, gate floor `0.899392`, `0/4` folds

No Price Path candidate passed the registered promotion boundary. Conditional
nested confirmation remained locked. No canonical code or schema was changed.

Controlled report:

- `training/output/expanded_20260716/price_path_state_controlled.json`
