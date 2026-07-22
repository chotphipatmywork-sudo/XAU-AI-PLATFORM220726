# CR-007 Proposed 16-Bar Price Path State

Version: 1.0.0

Date: 2026-07-16

Status: Rejected after controlled Train-only evidence

Architecture Baseline: ABR-1.0

Related Phase: Post-Phase-7 Model Improvement Research

## Evidence basis

CR-006 showed a small controlled improvement from completed-candle and combined
price-action context, but direct 1/4/16-bar displacement did not pass the
promotion gate. A displacement contains only the endpoints; it cannot
distinguish an efficient directional path from a highly reversing path that
finishes at the same close.

The approved Label observes the first `+/-1.5 ATR(14)` barrier reached during
the next 16 M15 bars. A past-only description of path efficiency and
persistence over the matching prior 16 bars is therefore the next bounded
information test.

## Research fields

All values use completed bar `t` and older bars only:

### Trend path

1. `path_directional_efficiency`: signed net close displacement divided by
   total absolute close travel.
2. `up_close_ratio`: percentage of non-flat close changes that are positive.
3. `directional_run_balance`: longest positive run minus longest negative run,
   normalized by 16.
4. `return_sign_persistence`: same-direction versus opposite-direction adjacent
   close changes.

### Volatility path

5. `path_travel_atr`: total absolute close travel over 16 changes relative to
   current ATR(14).
6. `range_efficiency`: completed 16-bar high-low range relative to close travel.
7. `range_expansion`: high-low range of bars `t..t-7` relative to bars
   `t-8..t-15`.

Signed unit values map `-1..1` to `0..100`. Ratios and percentages are clamped
to `0..100`. No label, future bar, Validation, Test, Risk, confidence,
execution result, or trade outcome is permitted.

## Fixed controlled comparison

Registered candidates:

1. `schema4_baseline`
2. `trend_path_state`: Baseline plus the four Trend-path fields
3. `volatility_path_state`: Baseline plus the three Volatility-path fields
4. `all_price_path_state`: Baseline plus all seven fields

The fixed estimator is raw `random_forest_depth_5_balanced`, policy is argmax,
and evaluation uses four Train-only expanding folds with the approved
16-record purge.

Promotion requires:

- ranking above Baseline by the registered weakest-gate rule;
- gate-floor improvement of at least `0.01`;
- no aggregate Macro F1 decrease;
- at least one complete passing fold.

## Nested and architecture gate

Nested confirmation is authorized only for one controlled-promoted candidate.
It uses three Inner folds inside each of four unseen Outer periods. Canonical
change evidence requires the candidate to be selected in all four Outer
histories and all four Outer gates to pass.

Even a research pass cannot change Runtime or Feature Schema without separate
approval, live/historical parity, full Dataset regeneration, complete
validation, and later untouched evaluation.

## Rollback

Delete the research engine, exporter, tests, CSV, reports, and this proposal.
Runtime and Feature Schema 4.0 remain unchanged.

## Approval record

- bounded research-only implementation: approved under the project owner's 2026-07-16 improvement authorization
- Runtime/Feature Schema change: not approved
- Validation/Test use: not approved
- deployment: not approved

## Controlled result

The exact 26,864-row auxiliary export matched the canonical Dataset keys and
provided 100% valid Price Path coverage. The fixed four-fold Train-only
comparison produced:

| Feature set | Macro F1 | Gate floor | Passing folds |
|---|---:|---:|---:|
| `schema4_baseline` | 0.394773 | 0.913112 | 0/4 |
| `trend_path_state` | 0.393123 | 0.911693 | 0/4 |
| `volatility_path_state` | 0.390513 | 0.902467 | 0/4 |
| `all_price_path_state` | 0.388547 | 0.899392 | 0/4 |

Baseline ranked first. No candidate improved the gate floor by `0.01`, no
candidate preserved or improved aggregate Macro F1, and no candidate passed a
complete fold. Therefore:

- `promoted_feature_set = null`;
- nested confirmation was not authorized and was not run;
- Feature Schema 4.0 and Runtime remain unchanged;
- Validation and Test remain unread;
- deployment remains unauthorized.
