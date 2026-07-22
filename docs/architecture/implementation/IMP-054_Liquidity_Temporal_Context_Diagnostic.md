# IMP-054 Liquidity Temporal Context Diagnostic

Status: Evaluated; proposal rejected before nested confirmation.

## Purpose

CR-003 tests whether past-only Liquidity event memory adds stable information beyond the current Schema 4.0 Liquidity snapshot. The experiment is offline, Train-only, and does not change MQL5 or the canonical Dataset.

## Derived values

Activity and range-position changes use a bounded delta with neutral at 50. Sweep means preserve the canonical `0/50/100` encoding over the latest 4 and 16 available observations. Buy-side and sell-side freshness equal 100 on the matching current sweep and decay linearly to zero after 16 observations without a matching sweep.

All values are bounded to `0..100` and use only the current and earlier rows.

## Controlled boundary

- fixed model: raw `random_forest_depth_5_balanced`
- fixed policy: argmax
- folds: four expanding Train-only folds
- purge: 16 records
- feature sets: Baseline, Liquidity Changes, Sweep Memory, All Liquidity Temporal

Promotion to nested confirmation follows the four predeclared conditions in CR-003. The experiment cannot authorize a Feature Contract or deployment change.

## Validation

`training/test_liquidity_temporal_diagnostic.py` must verify bounded deltas, sweep means, freshness decay, future-row isolation, exact feature-set boundaries, and active contract metadata before the project Dataset is evaluated.

## Result

The focused test passed. Baseline ranked above Sweep Memory, Liquidity Changes, and All Liquidity Temporal. Baseline Macro F1 was `0.3948`; the candidates produced `0.3926`, `0.3906`, and `0.3895`. No feature set passed a complete fold.

None of the candidates met the CR-003 promotion requirements. Nested confirmation was not authorized, Feature Schema 4.0 remains unchanged, and deployment remains closed.
