# IMP-056 Confirmed Swing Structure Research

Status: Evaluated; proposal rejected before nested confirmation.

## Source audit

The Trend package currently computes Structure, BOS, and CHOCH internally. Structure and BOS are slope-derived, while CHOCH is a documented future-phase default. `CTrendAssembler` already accepts these results and contains CHOCH-aware scaling, so genuine confirmed swing context is the next credible information gap inside the approved Trend group.

## Fixed research configuration

- timeframe: canonical M15 Dataset timestamps
- pivot left bars: `2`
- pivot confirmation/right bars: `2`
- search lookback: `64` closed observations
- output values: Structure Direction, Break Direction, CHOCH Direction, Structure Range Position

Parameters are fixed before Dataset evidence is inspected. Only confirmed pivots whose required confirmation bars are closed at the observation time are valid.

Rows without two confirmed highs and lows inside the fixed lookback remain
available as explicit neutral `50` values with `structure_valid=0`. The Python
join accepts those rows only when every research value is neutral and reports
confirmed coverage separately. The validity flag is metadata and is not a
candidate model input.

## Protected boundary

The research engine and exporter do not alter `CTrendAnalyzer`, `CTrendResult`, `CBrainFeatureAdapter`, the Dataset Writer, AI Runtime, Decision, Risk, or Execution. Canonical integration is prohibited until CR-005 research passes and a separate explicit approval is recorded.

## Required validation

- one class per `.mqh` file;
- focused MetaEditor test;
- zero compile errors and warnings;
- auxiliary ID/Timestamp join validation;
- bounded output validation;
- Train-only controlled and nested evidence;
- documentation and checksums.

## Predeclared controlled comparison

The Train-only diagnostic uses the same four expanding folds and 16-record
label-horizon purge as the active offline process. The fixed estimator is raw
`random_forest_depth_5_balanced` with argmax policy.

The only registered feature sets are:

- `schema4_baseline`: the twelve canonical Schema 4.0 values;
- `structure_core`: Baseline plus confirmed Structure, Break, and CHOCH direction;
- `all_swing_structure`: Structure Core plus confirmed swing-range position.

Promotion requires ranking above Baseline, a gate-floor improvement of at least
`0.01`, no Macro F1 reduction, and at least one complete passing fold. The
diagnostic must set `nested_confirmation_authorized=false` when any condition
fails.

The nested confirmation script is registered before controlled evidence is
available. It refuses to run unless the controlled report authorizes exactly
one promoted non-Baseline feature set. It then compares only Baseline versus
that promoted set using three Inner folds inside each of four unseen Outer
periods. Canonical-change evidence requires the promoted set to be selected in
all four Outer histories and every Outer gate to pass.

## Implemented files

- `core/brain/trend/models/ConfirmedSwingStructureResult.mqh`
- `core/brain/trend/engines/ConfirmedSwingStructureEngine.mqh`
- `core/ai/HistoricalSwingStructureExporter.mqh`
- `tests/TestHistoricalSwingStructureExporter.mq5`
- `tools/sync_swing_structure_research_to_mt5.ps1`

The exporter writes `XAU_AI_SWING_STRUCTURE_RESEARCH.csv` in the MT5 Files directory and removes itself after completion.

## Compile evidence

Workspace MetaEditor compile:

`Result: 0 errors, 0 warnings, 1222 ms elapsed, cpu='X64 Regular'`

Log:
`training/output/expanded_20260716/compile_swing_structure.log`

Python regression after the strict join and neutral-coverage implementation:

After registering the controlled and conditional nested diagnostics:

`PYTHON TESTS PASSED: 25/25`

## Export and controlled evidence

The compiled exporter ran successfully:

- synthetic structure valid: true
- closed-bar timing valid: true
- records written: `26,864`
- exact canonical ID/Timestamp order match: true
- duplicate/invalid rows: `0/0`
- confirmed coverage: `99.26%`

Controlled Train-only evidence ranked Schema 4.0 Baseline first:

- Baseline Macro F1 / gate floor: `0.3948 / 0.9131`
- All Swing Structure: `0.3924 / 0.9110`
- Structure Core: `0.3870 / 0.8951`
- complete passing folds: `0/4` for every feature set

No feature set met the registered promotion boundary. Nested confirmation
correctly remained unauthorized. Runtime, Feature Schema 4.0, Validation,
Test, and deployment are unchanged.
