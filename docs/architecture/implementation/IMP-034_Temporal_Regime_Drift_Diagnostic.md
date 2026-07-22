# IMP-034 Temporal Regime Drift Diagnostic

Status: Implemented and evaluated on nested Train-only Outer folds.

## Purpose

The nested purged estimate in IMP-033 showed materially weaker unseen-period performance than ordinary walk-forward selection. `training/temporal_regime_diagnostic.py` reproduces each already-selected Outer configuration and separates feature-distribution shift, label shift, prediction collapse, Session performance, and numeric regime performance without reading Validation or Test.

## Method

- Refit only the model and policy already selected inside each Outer history.
- Reproduce the recorded Outer metrics exactly before producing diagnostics.
- Measure every dimension in the active Feature Schema with a standardized mean difference between Outer history and evaluation.
- Report fixed SELL/HOLD/BUY label and prediction distributions.
- Break metrics down by Session and low/middle/high Trend, Volatility, and Liquidity activity buckets.
- For calibrated selections, compare the same model and policy using raw probabilities as a diagnostic-only counterfactual.

The diagnostic does not reselect a candidate, change a label, alter the feature contract, or authorize deployment.

## Focused validation

`training/test_temporal_regime_diagnostic.py` verifies active contract-version metadata, standardized shift, fixed class distributions, numeric regime buckets, and segmented metrics. This prevents a Schema 4.0 diagnostic from emitting stale Schema 3.0 evidence metadata.

## Result

The strongest mean distribution shift occurred in the Trend group:

| Feature | Mean absolute standardized shift | Maximum |
| --- | ---: | ---: |
| trend_regime | 0.3447 | 0.6960 |
| trend_momentum | 0.1831 | 0.3009 |
| trend_slope | 0.1744 | 0.3602 |
| liquidity_range_position | 0.0897 | 0.1489 |

Every other dimension had mean absolute shift below `0.052`. This indicates that temporal instability is concentrated in the Trend representation rather than broad dataset corruption.

Fold 2 used a calibrated depth-5 balanced forest with SELL minimum `0.35` and BUY minimum `0.50`. Although its true labels contained `41.9%` BUY, calibrated inference emitted `100%` SELL. Mean calibrated probabilities were SELL `0.5735`, HOLD `0.0824`, BUY `0.3441`. The same raw model and policy avoided SELL-only collapse but emitted only `4.6%` BUY and achieved BUY recall `0.0451`. Therefore both calibration transfer and the selected threshold were unstable across that temporal boundary.

Fold 4 used raw argmax and still produced BUY precision `0.3348`, showing that removing calibration alone is insufficient. New York Session BUY precision fell to `0.1833`, while Asia was `0.4419`, which supports further regime-aware investigation but is not causal evidence.

## Decision

Do not change labels or open Validation/Test. Do not deploy calibrated or raw locked artifacts. The next bounded experiment should compare expanding history with purged rolling or recency-weighted Train-only histories. This directly tests whether older Trend regimes are degrading generalization while preserving the approved four feature groups and runtime boundaries.

## Expanded-history result

IMP-053 reran this diagnostic against the 18,788-record expanded Train partition and its registered nested report. The output correctly identifies Training/Feature/Label contracts `4.0.0/4.0.0/1.1.0`; Validation and Test remained unread.

Trend remained the dominant temporal shift:

| Feature | Mean absolute standardized shift | Maximum | Folds >= 0.25 |
| --- | ---: | ---: | ---: |
| trend_regime | 0.2511 | 0.3529 | 3 |
| trend_momentum | 0.1385 | 0.2598 | 1 |
| trend_slope | 0.1349 | 0.2666 | 1 |
| liquidity_range_position | 0.0573 | 0.1405 | 0 |

Every Session and Volatility dimension had a mean absolute shift below `0.014`. This again localizes the principal distribution transfer problem to Trend rather than broad Dataset corruption.

Expanded Outer Fold 2 covered `2025-11-21 05:30:00` through `2025-12-30 05:45:00`. The calibrated confidence configuration predicted HOLD for `88.84%` of rows even though the true HOLD ratio was only `13.33%`. It achieved Macro F1 `0.1507`, SELL recall `0.0544`, and BUY recall `0.0628`.

The diagnostic-only raw-probability counterfactual with the same model and policy improved Macro F1 to `0.3898`, SELL recall to `0.3970`, and BUY recall to `0.2851`, but still failed the complete gate. Calibration instability caused most of the Fold 2 collapse, while the remaining raw result confirms that removing calibration alone is insufficient.

The expanded diagnostic SHA-256 is `7A0BC9AD2E3BF72DE16A7A4F77BBD9F74A9B4137C63ACC6D4ABAE04814905016`.
