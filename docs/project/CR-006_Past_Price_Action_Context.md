# CR-006 Proposed Past Price Action Context

Version: 0.1.0

Date: 2026-07-16

Status: Research evaluated and rejected; no Runtime or Feature Schema change

Architecture Baseline: ABR-1.0

Related Phase: Post-Phase-7 Model Improvement Research

## Problem

Source audit after CR-003 through CR-005 found that Feature Schema 4.0
represents:

- Trend through EMA 50/200 separation, EMA-50 movement over 16 bars, and
  one-bar EMA slope;
- Volatility through current ATR relative to previous and 16-bar ATR history;
- Liquidity through relative volume, ten-bar range position, and sweep state;
- Session through one-hot state and progress.

The approved Label uses the close of the current M15 bar and tests which
`+/-1.5 ATR(14)` barrier is reached first during the next 16 bars. The model
does not directly receive the completed price displacement over the prior
1/4/16 bars, the completed candle impulse, or the width and position of the
immediately preceding 16-bar price range.

## Research boundary

Create a research-only auxiliary export from bars known at the Dataset
observation close. The fields remain inside the approved semantic groups:

### Trend

- `price_return_1_atr`
- `price_return_4_atr`
- `price_return_16_atr`

Signed displacement is ATR-normalized and bounded to `0..100`, with `50`
neutral and saturation at `+/-2 ATR`.

### Volatility

- `candle_body_atr`
- `candle_range_atr`
- `candle_close_location`

The signed body uses the same neutral encoding. Range is positive
ATR-normalized and close location is bounded inside the completed candle.

### Liquidity

- `prior_range_width_atr`
- `prior_range_position`

The range uses only the 16 bars before the feature bar. Width is
ATR-normalized; position is the current close relative to that completed past
range.

No future bar, label, Validation, Test, Risk, confidence, execution result, or
trade outcome may enter the auxiliary file.

## Fixed controlled comparison

The candidate grid is registered before evidence:

1. `schema4_baseline`
2. `direct_price_momentum`: Baseline plus the three Trend displacement fields
3. `completed_candle_impulse`: Baseline plus the three Volatility/candle fields
4. `prior_range_context`: Baseline plus the two Liquidity range fields
5. `all_price_action_context`: Baseline plus all eight fields

The fixed estimator is raw `random_forest_depth_5_balanced`, policy is argmax,
and evaluation uses four Train-only expanding folds with a 16-record purge.

Promotion requires:

- ranking above Baseline by the registered weakest-gate selection rule;
- gate-floor improvement of at least `0.01`;
- no aggregate Macro F1 decrease;
- at least one complete passing fold.

## Nested and architecture gate

Nested confirmation may compare only Baseline and the single controlled
promoted feature set. Three Inner folds select inside each of four unseen
Outer periods. Canonical-change evidence requires the promoted set to be
selected in all four Outer histories and every Outer gate to pass.

Even a research pass does not authorize Runtime integration. Integration
requires separate architecture approval, a Feature Schema version review,
live/historical parity, complete Dataset regeneration, full validation, and
later untouched evaluation.

## Risks

- Direct returns may still be unstable across market regimes.
- Range position overlaps part of the existing Liquidity representation.
- ATR normalization can suppress absolute-price regime information.
- Inspected Train periods are development evidence, not deployment evidence.

## Rollback

Delete the research exporter, tests, auxiliary CSV, diagnostics, and this
proposal. Runtime and Feature Schema 4.0 remain unchanged.

## Approval record

- bounded research-only export and diagnostic: approved under the project owner's 2026-07-16 improvement authorization
- Runtime/Brain public behavior change: not approved
- Feature Schema change: not approved
- Validation/Test use: not approved
- deployment: not approved

## Export validation

The auxiliary export completed with `26,864` records:

- exact Dataset ID/Timestamp order match: true
- duplicate keys: `0`
- invalid or out-of-range rows: `0`
- valid context coverage: `26,864/26,864` (`100%`)
- synthetic encoding and closed-bar timing tests: true

## Controlled result

The fixed comparison evaluated `9,394` purged Train-only forward rows:

| Feature set | Macro F1 | Gate floor | BUY precision | Passing folds |
| --- | ---: | ---: | ---: | ---: |
| All Price Action | 0.3970 | 0.9207 | 0.5058 | 0 |
| Completed Candle Impulse | 0.3973 | 0.9197 | 0.5023 | 0 |
| Schema 4.0 Baseline | 0.3948 | 0.9131 | 0.4938 | 0 |
| Prior Range Context | 0.3922 | 0.9110 | 0.4994 | 0 |
| Direct Price Momentum | 0.3914 | 0.9070 | 0.5012 | 0 |

All Price Action improved the weakest-gate ratio by approximately `0.0076`,
below the registered `0.01` minimum. Completed Candle Impulse improved Macro
F1 modestly, but no candidate passed a complete fold.

## Decision

Reject CR-006 as a canonical Feature Schema change.
`promoted_feature_set=null` and
`nested_confirmation_authorized=false`. Do not run nested confirmation, do not
change Runtime or Feature Schema 4.0, do not regenerate the canonical Dataset,
and do not deploy.
