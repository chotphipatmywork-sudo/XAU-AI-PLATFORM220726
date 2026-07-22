# IMP-055 Temporal Brain Feature Window Diagnostic

Status: Evaluated; proposal rejected before nested confirmation.

## Purpose

CR-004 tests complete past Brain states instead of adding another manually designed indicator. The diagnostic appends exact prior Schema 4.0 rows at fixed observation lags and evaluates them under the existing purged Train-only process.

## Leakage boundary

For row `t`, lag `n` reads only row `t-n`. Early rows reuse the earliest available row. Changing a later row must never change any earlier transformed row. Purged feature observations immediately before evaluation may be used because they would have been observable in live inference; their labels remain excluded.

## Fixed comparison

- Baseline: 12 current values
- Lag 1: 24 values
- Lags 1+4: 36 values
- Lags 1+4+8: 48 values
- model: raw depth-5 balanced random forest
- policy: argmax
- evaluation: four Train-only folds, 16-record purge

The CR-004 promotion gate is applied automatically. No Runtime, Dataset, or deployment change is permitted by this diagnostic.

## Validation

`training/test_temporal_feature_window_diagnostic.py` must verify exact lag values, early-row handling, future-row isolation, tensor dimensions, the fixed candidate boundary, promotion rules, and active contract metadata.

## Result

The focused test passed. Lags 1+4 ranked first and raised Macro F1 from Baseline `0.3948` to `0.4036`, but its gate-floor improvement was only `0.0047` and it passed `0/4` complete folds. The required promotion improvement was `0.01` with at least one passing fold.

`promoted_feature_set=null` and `nested_confirmation_authorized=false`. The canonical snapshot contract remains unchanged.
