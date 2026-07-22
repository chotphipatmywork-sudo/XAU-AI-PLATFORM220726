# IMP-030 Train-Only Walk-Forward Feature Diagnostic

Status: Schema 2.0.0 diagnostic evaluated; tool updated and validated for active Schema 3.0.0.

## Purpose

Feature Contract 2.0 improved aggregate Macro F1 and BUY/HOLD recall, but the Train-only walk-forward selection still failed BUY precision and no fold passed the complete evaluation gate. This diagnostic was introduced to identify which approved dimensions contribute consistently across time. It now follows the active Feature Contract 3.0 eleven-dimension order.

## Method

`training/walk_forward_feature_diagnostic.py` reads only the Train CSV and the Train-only `walk_forward_diagnostics.json` selection report. It rebuilds the selected candidate independently in the same four expanding chronological folds. Within each forward evaluation block it permutes each continuous feature independently and permutes the three Session one-hot columns together so every synthetic row remains a valid Session. It measures the resulting drop in:

- Macro F1
- BUY precision
- BUY recall

The report retains every fold result and records how many folds have a positive drop. This prevents a strong result in one market period from hiding instability in the others.

## Boundaries

- Validation and Test paths are not accepted by the command.
- The diagnostic does not modify CSV files, select a new model, or authorize deployment.
- The diagnostic does not change active Feature Contract 3.0 or Label Schema 1.1.0.
- AI Runtime, Decision, Risk, Execution, and Trade Lifecycle remain unchanged.
- Permutation importance is an association diagnostic, not proof of causal trading value.

## Validation

Run `training/test_walk_forward_feature_diagnostic.py`. The focused test creates an eleven-dimensional synthetic dataset with a known signal, valid Liquidity sweep encoding, and valid Session one-hot rows. It verifies that permutation importance ranks the signal above noise and preserves positive-fold counts.

## Historical Feature Contract 2.0 result

The focused test passed. The Train-only diagnostic reproduced the selected walk-forward baseline exactly over 2,336 evaluation records: Macro F1 `0.4140`, BUY precision `0.4192`, and BUY recall `0.4225`. Validation and Test were not read.

| Feature | Mean Macro-F1 drop | Positive folds | Mean BUY-precision drop | Positive folds |
| --- | ---: | ---: | ---: | ---: |
| `session_one_hot` | 0.0477 | 4/4 | -0.0060 | 3/4 |
| `trend_regime` | 0.0229 | 3/4 | 0.0191 | 3/4 |
| `liquidity` | 0.0196 | 4/4 | 0.0095 | 2/4 |
| `trend_momentum` | 0.0138 | 4/4 | 0.0183 | 3/4 |
| `volatility` | 0.0107 | 4/4 | 0.0066 | 2/4 |
| `trend_slope` | 0.0048 | 2/4 | 0.0097 | 3/4 |

The complete Session group is the strongest contributor to overall Macro F1 and is positive in all folds, but it does not improve BUY precision on average. Trend regime and medium momentum are the strongest contributors to BUY precision. Liquidity and Volatility contribute positively to Macro F1 in all folds but are less consistent for BUY precision. These results support retaining Session for class balance while investigating stronger directional information inside the existing Liquidity and Volatility groups before changing labels or deployment policy.
