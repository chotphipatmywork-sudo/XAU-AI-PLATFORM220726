# IMP-036 Feature-Label Stability Diagnostic

Status: Implemented and evaluated on four Train-only Outer periods.

## Purpose

Expanding history outperformed static rolling and recency weighting, while temporal drift remained concentrated in Trend features. `training/feature_label_stability_diagnostic.py` tests whether identical approved feature regimes retain the same SELL/HOLD/BUY relationship across non-overlapping Train Outer periods without fitting a model.

## Method

- Continuous dimensions in the active Feature Schema are grouped into fixed low/middle/high buckets, including Schema 4.0 Session Progress.
- Liquidity sweep uses down/neutral/up and Session uses Asia/London/New York.
- Each bucket reports SELL/HOLD/BUY ratios for each Outer period.
- Cross-period instability uses pairwise Jensen-Shannon divergence and the maximum BUY-rate range.
- Ordered dimensions additionally report `BUY(high) - BUY(low)` and whether its sign changes across periods.
- A bucket must contain at least 30 records in at least three periods to enter the stability summary.

The diagnostic reads only Train and the already-created nested report. It does not fit or select a model, change labels, or authorize deployment.

## Focused validation

`training/test_feature_label_stability_diagnostic.py` verifies active contract-version metadata, inclusion of Session Progress, zero divergence for identical distributions, positive divergence after material drift, fixed bucket class ratios, and detection of directional relationship reversal.

## Result

The most unstable approved relationships were Trend Regime, Volatility Regime, Session, Trend Slope, and Trend Momentum.

| Feature/group | Mean pairwise JS | Maximum BUY-rate range | Direction sign |
| --- | ---: | ---: | --- |
| trend_regime | 0.0192 | 0.2403 | Negative in 4/4 periods |
| volatility_regime | 0.0174 | 0.3895 | Changed, 2 positive / 2 negative |
| session | 0.0170 | 0.2393 | Not ordered |
| trend_slope | 0.0148 | 0.2844 | Changed, 2 positive / 2 negative |
| trend_momentum | 0.0122 | 0.2365 | Changed, 2 positive / 2 negative |

For Trend Regime, `BUY(high) - BUY(low)` was `-0.0735`, `-0.0774`, `-0.0775`, and `-0.0912`. The inverse association is small but exceptionally consistent. Source review confirmed that LabelGenerator maps the upper barrier to BUY and the lower barrier to SELL, while Trend Regime maps positive EMA separation above 50 and negative separation below 50. This is therefore not a reversed enum or CSV mapping bug.

The likely interpretation is horizon/context mismatch: a strong established EMA regime can represent a mature move over the next 16 M15 bars, while low Trend Regime may precede rebound behavior. Trend Momentum and Trend Slope changed sign across periods, so no single scalar threshold captures that behavior reliably.

Volatility Regime also reversed directional association across periods, and Session BUY rates changed materially, especially Asia and New York. These effects make a static probability threshold or one-dimensional rule unsafe.

## Decision

Do not invert Trend Regime, change Label Schema 1.1, or add Session trading rules. The next bounded experiment should derive Trend-group interaction candidates from the existing replayed Brain values, such as regime/momentum agreement, regime/slope agreement, extension from neutral, and disagreement pressure. These candidates must first be evaluated offline with purged nested methodology before any Feature Contract or MQL5 change is proposed.

## Expanded-history result

The Schema 4.0 diagnostic was repeated on the four expanded Train Outer periods. Validation and Test were not read.

| Feature/group | Mean pairwise JS | Maximum BUY-rate range | Direction sign |
| --- | ---: | ---: | --- |
| session | 0.0103 | 0.1212 | Not ordered |
| trend_regime | 0.0085 | 0.1894 | Changed, 2 positive / 2 negative |
| trend_slope | 0.0060 | 0.1015 | Changed, 1 positive / 3 negative |
| session_progress | 0.0057 | 0.1139 | Positive in 4/4 periods |
| liquidity_range_position | 0.0050 | 0.0935 | Negative in 4/4 periods |

The expanded periods reduce average divergence relative to the earlier short-history experiment, but the directional Trend Regime relationship still changes sign. This confirms that inverting Trend or applying one fixed Trend threshold remains unsafe.

Session Progress is directionally consistent across all four expanded periods, while the categorical Session group has the highest overall relationship instability. Session Progress therefore remains justified as part of Schema 4.0, but its existing information is not sufficient for deployment: the complete nested process still passed `0/4` Outer gates.

Any next experiment must add credible past-only information or a predeclared inductive bias inside the canonical feature groups. It must not convert these associations directly into trading rules or consume Validation/Test.
