# IMP-063 Completed-Tick Microstructure Research

Status: Controlled evidence complete; rejected.

Related: CR-011, Feature Schema 4.0, Label Schema 1.1.0, Phase 8A closure

## Purpose

Test whether completed M15 tick information adds stable Train-only predictive
value after bar-level research and both Shadow inference providers failed their
quality gates. This implementation is isolated research and does not alter the
canonical Brain, Runtime, Decision, Risk, Execution, or Trade Lifecycle.

## Completed-bar contract

For Dataset bar `t`, only ticks whose millisecond timestamps are inside
`[open(t), open(t) + 15 minutes)` are accepted. ATR(14) is read at the same
completed M15 bar. A row is invalid if timing, quotes, tick count, ATR, or tick
movement is insufficient.

The research fields are signed tick-direction imbalance, burst concentration
across fifteen one-minute buckets, mean and maximum spread divided by ATR,
realized tick travel relative to ATR, and first-to-last path efficiency.

All candidate fields are encoded from 0 to 100. Invalid rows contain six
neutral `50` values, their observed non-negative tick count, and validity `0`.
Tick count and validity are metadata and are never candidate model inputs.

## Isolation and leakage controls

- Output is `XAU_AI_TICK_MICROSTRUCTURE_RESEARCH.csv`.
- Canonical Feature Schema 4.0 remains unchanged.
- Exact Dataset ID and timestamp matching is mandatory.
- The diagnostic reads only the purged Train partition and auxiliary context.
- Validation and Test are not read.
- Four chronological folds and the 16-bar purge are fixed.
- Completed-tick coverage below 80% rejects the diagnostic.

## Fixed comparison

The grid is `schema4_baseline`, `liquidity_tick_flow`,
`volatility_tick_state`, and `all_tick_microstructure`. Every candidate uses
`random_forest_depth_5_balanced`, raw probabilities, and argmax.

Promotion requires Macro F1 improvement of at least 0.01, no gate-floor
degradation, improvement in at least two chronological folds, and no aggregate
BUY/SELL precision or recall degradation. Passing authorizes only nested
confirmation, not a schema change or deployment.

## Implemented files

- `core/brain/liquidity/models/TickMicrostructureResult.mqh`
- `core/brain/liquidity/engines/TickMicrostructureEngine.mqh`
- `core/ai/HistoricalTickMicrostructureExporter.mqh`
- `tests/TestHistoricalTickMicrostructureExporter.mq5`
- `tools/sync_tick_microstructure_research_to_mt5.ps1`
- `tools/compile_tick_microstructure_research.ps1`
- `training/tick_microstructure_diagnostic.py`
- `training/test_tick_microstructure_diagnostic.py`

## Safety state

- Forward provider: Legacy development heuristic NO-GO.
- Directional provider: Strategy Tester-only and rejected.
- model deployment authorized: false.
- live execution authorized: false.
- broker mutation authorized: false.

## Pre-export validation

- focused Python diagnostic test: passed;
- complete Python regression: 33/33 passed;
- PowerShell sync/compile tooling parse: passed;
- workspace/MT5 SHA-256 verification: all four research files match;
- MetaEditor focused exporter compile: 0 errors, 0 warnings;
- historical tick export: 26,864 records written.

## Export evidence

- total auxiliary records: 26,864;
- valid completed-tick records: 26,859;
- neutral invalid records: 5;
- valid coverage: 99.9814%;
- minimum/maximum observed tick count: 0/15,730;
- duplicate or missing Train joins: 0.

## Controlled Train-only evidence

The fixed ranking was:

1. `schema4_baseline`: Macro F1 `0.394773`, gate floor `0.913112`, `0/4` folds;
2. `liquidity_tick_flow`: Macro F1 `0.387090`, gate floor `0.893005`, `0/4` folds;
3. `volatility_tick_state`: Macro F1 `0.357245`, gate floor `0.804532`, `0/4` folds;
4. `all_tick_microstructure`: Macro F1 `0.353290`, gate floor `0.794834`, `0/4` folds.

Validation dataset used: false. Test dataset used: false. Future rows used:
false. Every completed-tick candidate reduced both Macro F1 and the complete
gate floor relative to Baseline. No candidate improved at least two folds while
preserving BUY/SELL coverage.

CR-011 is rejected. Nested confirmation remains locked, canonical Feature
Schema 4.0 is unchanged, and no inference or deployment code is authorized.

Controlled report:

- `training/output/expanded_20260716/tick_microstructure_controlled.json`
