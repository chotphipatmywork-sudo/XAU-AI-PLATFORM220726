# IMP-087 Existing Entry Geometry Outcome Attribution

Version: 1.1.0

Date: 2026-07-23

Status: Completed; no geometry view eligible

Architecture Baseline: ABR-1.0

Related: ADR-006, RSCS-1.0, IMP-079, IMP-083, IMP-086

## Purpose

Test whether deterministic structural evidence already known when an accepted
Setup was created distinguishes Target-first from Stop-first outcomes. This is
an offline Train-only evidence audit, not a new AI Feature Schema, threshold,
Entry rule, Risk rule, Runtime Candidate, or Change Request.

## Frozen evidence

- pre-Train Setup Audit SHA-256:
  `A406B7EDADA6CACB5691487341294E5F950FF262D1CE8AE26EF958843338B8B8`;
- main Train Setup Audit SHA-256:
  `A8463D7F118CB52A7B514099FF8B8839F3C2401ECA5A66F50376C4D87C1C9F7A`;
- augmented Train SHA-256:
  `F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E`;
- Effective Sample audit SHA-256:
  `2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414`;
- IMP-086 diagnostic SHA-256:
  `A281F29D0CD25E9DCE894BF03F486BA6F7426014DF4F1BFD31DFA29BAA0DBC27`;
- Past-only Target request manifest SHA-256:
  `2D6A559F03245D40C0CB84ACAC1CC1C97D6F2017875ED3DF513D5C54F9C4C6BF`.

Only the 232 maximum non-overlapping Effective Train records may be joined.
The join key is exact `observation_time`; direction, Entry, Stop, Target,
cost-aware RR, minimum RR, estimated cost, and structural levels must pass
numeric parity. Missing, duplicated, non-chronological, or ambiguous evidence
fails closed. Validation and Test paths are forbidden inputs.

## Frozen evidence fields

All values are available at the accepted Setup observation:

1. `sweep_penetration_atr` from Setup Audit V1;
2. `reclaim_distance_atr` from Setup Audit V1;
3. `reclaim_sweep_balance = reclaim / (sweep + reclaim)`;
4. `entry_to_poi_r = abs(entry - reference_poi) / gross_risk_price`;
5. `poi_to_stop_r = abs(reference_poi - stop) / gross_risk_price`;
6. `gross_reward_r = abs(target - entry) / gross_risk_price`;
7. `cost_fraction_gross_risk = estimated_cost_points / risk_points`;
8. `cost_aware_plan_rr` from the accepted plan.

Every denominator must be positive and every derived value finite. POI must be
between Entry and structural Stop in the directionally valid geometry. This
diagnostic may not repair or infer invalid evidence.

## Frozen views

- `full_geometry_control`: all eight fields;
- `trigger_shape`: fields 1-3;
- `entry_invalidation_geometry`: fields 4-5;
- `payoff_geometry`: fields 6-8.

The full view is a diagnostic control and cannot be promoted. No approved
canonical Trend, Volatility, Liquidity, or Session feature is changed or
extended; these fields remain deterministic Setup/Trade Plan evidence.

## Past-only method

- outcome classes are exactly `STOP_FIRST` and `TARGET_FIRST`;
- four expanding chronological folds with the first 50% as initial history;
- each evaluation row is compared only with mature earlier outcomes;
- standardization is fitted on past reference rows only;
- 15 nearest past neighbours with Euclidean distance and deterministic class
  tie order;
- report true-class support gain over past historical class frequency,
  nearest-class match, balanced Accuracy, Macro F1, per-class recall, and the
  same support-gain statistic separately for BUY and SELL;
- report outcome counts and mean/median evidence values descriptively, without
  converting them into thresholds.

## Frozen hypothesis-readiness gate

A non-control view is eligible only if all are true:

- aggregate true-class support gain is at least `0.03`;
- balanced Accuracy is at least `0.55`;
- Macro F1 and nearest-class match are each at least `0.50`;
- support gain is positive in all four folds;
- recall is at least `0.30` for both outcome classes;
- BUY and SELL support gains are both positive.

If multiple views pass, rank by minimum class recall, minimum direction support
gain, aggregate support gain, Macro F1, balanced Accuracy, then view name
ascending. At most the first view may be named for a separately pre-registered
confirmation. Passing does not authorize a threshold, Candidate, Runtime
change, Validation access, Forward, or Deployment.

## Safety and validation plan

Add a focused synthetic test for geometry parity, directional POI placement,
past-only binary separation, readiness gates, and fail-closed invalid values.
Run the complete Python regression afterward. No MQL5 source is changed, so
the last affected compile remains IMP-084 `0 errors, 0 warnings`.

Validation/Test/Forward/Live/Deployment remain sealed and status remains
`OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO`.

## Completed evidence

All frozen hashes passed. The strict join reproduced exactly 232 Effective
Train records: 173 `STOP_FIRST` and 59 `TARGET_FIRST`. Entry, Stop, Target,
POI, structural levels, cost-aware RR, minimum RR, point size, and estimated
cost all passed source/effective parity. No Validation or Test path was read.

The diagnostic Artifact SHA-256 is
`40B1A1D46F7C20A960C22AD60FC4B4FEF612DAAA569BCDBE823AACB5FA60E039`.

## Past-only result

| View | Support gain | Balanced Accuracy | Macro F1 | Positive folds | Stop recall | Target recall | BUY gain | SELL gain | Ready |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Full control | -0.0149 | 0.492 | 0.443 | 0/4 | 0.926 | 0.057 | -0.0419 | +0.0150 | no |
| Trigger Shape | -0.0069 | 0.494 | 0.408 | 2/4 | 0.988 | 0.000 | -0.0244 | +0.0126 | no |
| Entry/Invalidation | -0.0017 | 0.514 | 0.441 | 1/4 | 1.000 | 0.029 | -0.0146 | +0.0126 | no |
| Payoff Geometry | +0.0017 | 0.514 | 0.441 | 2/4 | 1.000 | 0.029 | +0.0084 | -0.0056 | no |

No view approached the frozen `+0.03` support-gain requirement or `0.55`
balanced-Accuracy requirement. Every eligible view effectively predicted the
majority Stop class and failed the minimum Target recall. Direction evidence
also reversed: Trigger and Entry/Invalidation were negative for BUY, while
Payoff Geometry was negative for SELL.

Descriptive means were directionally modest rather than decisive. Target-first
records had lower sweep penetration (`0.234` versus `0.261` ATR), higher
reclaim distance (`0.335` versus `0.301` ATR), slightly lower cost fraction
(`0.221` versus `0.240`), and lower cost-aware plan RR (`2.641` versus `2.951`).
These differences did not survive the past-only gate and cannot be converted
into thresholds.

## Decision and missing evidence

No geometry view is eligible for confirmation. No reclaim, POI, cost, target,
or RR threshold; Candidate; CR; Feature Schema change; Runtime change; or Risk
change is authorized.

The existing V1 Setup snapshot proves accepted-plan geometry but does not
retain enough trigger-event path detail to explain Target-first outcomes. A
future evidence contract would need, before outcome use, past-only fields such
as M5 trigger OHLC/body/wicks/close position, POI-touch age, entry drift from
trigger close, and confirmed structural-level age. Adding that exporter/schema
is a separate MQL5 evidence-collection change and requires explicit approval;
it must remain offline and tester-only.

The focused test and complete Python regression passed `55/55`. No MQL5 file
changed, so the last affected MetaEditor result remains IMP-084 `0 errors, 0
warnings` and was not rerun.

RSCS-1.0 remains Research Quality `100`, Strategy Evidence `20`, Operational
Safety `100`, raw Overall `60`, and hard-gated Overall Readiness `49`. Status is
`NO_GO_TRAIN`, with zero score delta from IMP-086. The scorecard SHA-256 is
`96244169C3AC4087E69C19C6D2F105B055AFF46B00D1C245A6941AC6C054A65C`.
