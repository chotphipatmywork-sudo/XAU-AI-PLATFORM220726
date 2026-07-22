# IMP-050 Nested H1 Context Diagnostic

Status: Implemented and evaluated; complete H1 context rejected.

## Purpose

The fixed controlled comparison in IMP-049 showed mixed closed-H1 results across inspected Train folds. `training/nested_h1_context_diagnostic.py` prevents that inspected aggregate from selecting the feature set directly: three Inner folds choose Schema 4.0 Baseline or Schema 4.0 plus five closed-H1 fields separately before each of four unseen Outer periods.

## Fixed boundary

- model: `random_forest_depth_10_hold_2`
- probabilities: raw
- decision policy: argmax
- feature sets: exact Schema 4.0 Baseline versus Baseline plus five H1 Trend/Volatility values
- purge: 16 records at every Inner and Outer boundary
- inputs: Train and auxiliary H1 research CSV only

Selection uses the established stable-gate, folds-passing, aggregate-gate, weakest-gate, Macro F1, and Accuracy ordering. No model or policy search is added.

## Validation

`training/test_nested_h1_context_diagnostic.py` verifies the exact two-set boundary and weakest-gate selection. Existing nested-walk-forward tests cover fold and purge construction.

No result from this diagnostic can change the canonical Feature Contract or authorize deployment. CR-002 may advance to architecture review only if past-only Inner selection retains H1 context with credible Outer consistency.

## Result

Inner selection chose complete H1 context before Outer folds 1, 3, and 4, and chose Baseline before fold 2. Aggregate Outer Accuracy was `0.4326`, Macro F1 `0.3822`, SELL precision `0.4861`, BUY precision `0.3933`, and BUY recall `0.3839`. No Outer fold passed the complete gate.

Although H1 was selected in three histories, the mixed Outer process underperformed the fixed Schema 4.0 Baseline and failed temporal stability. The complete five-field proposal is rejected.
