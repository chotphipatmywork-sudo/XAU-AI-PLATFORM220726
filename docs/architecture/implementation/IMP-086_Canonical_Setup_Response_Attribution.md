# IMP-086 Canonical Setup Response Attribution

Version: 1.1.0

Date: 2026-07-23

Status: Completed; no hypothesis group eligible

Architecture Baseline: ABR-1.0

Related: Feature Schema 4.0.0, RSCS-1.0, IMP-036, IMP-041, IMP-084, IMP-085

## Purpose

Measure whether the approved canonical Trend, Volatility, Liquidity, and
Session features contain past-only information that distinguishes why the
same cost-covered Breakeven rule helps some accepted Setups and clips others.
Move diagnosis upstream to Setup/Entry quality without changing the Feature
Schema, Entry contract, Risk, lifecycle, Runtime, or Deployment state.

## Frozen evidence

- augmented Effective-Train source SHA-256:
  `F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E`;
- Effective Sample audit SHA-256:
  `2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414`;
- lifecycle request, M5 path, IMP-084 replay, and IMP-085 attribution hashes
  remain those frozen in IMP-085;
- only the 232 maximum non-overlapping Effective Train records are admissible;
- Validation/Test paths are forbidden inputs.

## Frozen response classes

Recompute the IMP-085 Breakeven `1.00x` paired transition for every record and
use exactly four response classes:

1. `STOP_UNCHANGED`;
2. `STOP_LOSS_IMPROVED_BY_MANAGEMENT`;
3. `TARGET_CLIPPED_BY_MANAGEMENT`;
4. `TARGET_PRESERVED`.

The class counts must exactly match the hash-sealed IMP-085 report. Ambiguity,
unresolved paths, key drift, feature drift, or class drift fails closed.

## Frozen canonical views

- `full_schema`: all 12 Schema 4.0 fields, as a diagnostic control;
- `trend_group`: Regime, Momentum, Slope;
- `volatility_group`: Regime, Change;
- `liquidity_group`: Activity, Range Position, Sweep Direction;
- `session_group`: Asia/London/New York one-hot and Session Progress.

No feature is inverted, reweighted, added, or removed from its approved group.

## Past-only separability method

- four expanding chronological folds;
- the first 50% is initial history and each remaining quarter-fold is evaluated
  only against earlier records;
- Effective Sample outcome intervals must prove the last reference outcome is
  mature before each evaluation starts, so no additional row purge is needed;
- standardization is fit on past reference rows only;
- 15 nearest past neighbours, Euclidean distance, deterministic class-order
  tie break;
- report true-class neighbour support, gain over historical class frequency,
  normalized entropy, nearest-class match, Accuracy, balanced Accuracy,
  Macro F1, and per-class precision/recall.

## Frozen hypothesis-readiness gate

A canonical group, excluding the full-schema control, may only become eligible
for a separately pre-registered confirmation if all are true:

- aggregate true-class support gain is at least `0.03`;
- aggregate balanced Accuracy and Macro F1 are both at least `0.30`;
- nearest-class match is at least `0.30`;
- support gain is positive in all four folds;
- recall is at least `0.15` for every response class.

Passing this gate does not authorize a filter, model, CR, Runtime change, or
Validation. If multiple groups pass, the fixed ranking is: minimum class
recall, then support gain, Macro F1, balanced Accuracy, and canonical group
name ascending. Only the first group may be named for a new confirmation
contract.

## Fixed-bucket explanation

Continuous fields use the existing fixed thirds: low `<33.333333`, middle
`<66.666667`, high otherwise. Liquidity Sweep uses down/neutral/up and Session
uses Asia/London/New York. Each bucket reports class counts, Baseline Target
rate, Target preservation rate, Stop improvement rate, Baseline/Candidate Mean
R, and Mean/Net Delta R. Buckets are descriptive and cannot become thresholds.

## Safety and validation plan

A focused synthetic test must cover canonical group boundaries, four-class
entropy/ties, past-only neighbourhood separation, readiness gates, and bucket
accounting. Complete Python regression follows. This stage changes no MQL5;
the last affected MetaEditor compile remains IMP-084 `0 errors, 0 warnings`.
Validation/Test/Forward/Live/Deployment remain sealed and unauthorized.

## Completed evidence

The strict join reproduced all 232 effective records and the frozen IMP-085
response counts exactly:

| Response class | Records |
| --- | ---: |
| Stop unchanged | 131 |
| Stop loss improved by management | 42 |
| Target clipped by management | 17 |
| Target preserved | 42 |

The completed diagnostic Artifact SHA-256 is
`A281F29D0CD25E9DCE894BF03F486BA6F7426014DF4F1BFD31DFA29BAA0DBC27`.
All source hashes, schema version `4.0.0`, request/path keys, features, outcome
intervals, and IMP-085 class totals passed fail-closed parity checks.

## Canonical-view result

| View | Support gain | Balanced Accuracy | Macro F1 | Nearest match | Positive folds | Minimum recall | Ready |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Full-schema control | -0.015 | 0.231 | 0.172 | 0.345 | 1/4 | 0.000 | no |
| Trend | -0.006 | 0.256 | 0.202 | 0.422 | 2/4 | 0.000 | no |
| Volatility | +0.007 | 0.287 | 0.259 | 0.431 | 1/4 | 0.000 | no |
| Liquidity | -0.015 | 0.233 | 0.189 | 0.345 | 1/4 | 0.000 | no |
| Session | -0.010 | 0.257 | 0.216 | 0.353 | 2/4 | 0.000 | no |

Volatility was the least weak view, but its support gain was `0.007` against
the frozen `0.03` requirement, balanced Accuracy was `0.287`, Macro F1 was
`0.259`, only one of four folds had positive support gain, and at least one
minority class had zero recall. The full-schema control mostly reproduced the
majority `STOP_UNCHANGED` class and did not rescue separability.

Fixed-bucket outputs remain post-hoc explanations. For example, high Session
Progress improved Breakeven Mean R relative to Baseline while the low and
middle buckets did not, but this pattern failed the past-only neighbourhood
gate and is not a permitted threshold or Session filter.

## Decision and score

No canonical group is eligible for a confirmation contract. No threshold,
filter, Candidate, model, Runtime change request, or deployment authority was
created. Validation and Test were not read; model training was not performed;
Runtime and Risk were unchanged.

The focused diagnostic test passed and the complete Python regression passed
`54/54`. This implementation changes no MQL5, so the last affected MetaEditor
result remains IMP-084 `0 errors, 0 warnings` and was not rerun.

RSCS-1.0 remains Research Quality `100`, Strategy Evidence `20`, Operational
Safety `100`, raw Overall `60`, and hard-gated Overall Readiness `49`. Status is
`NO_GO_TRAIN`; every score delta from IMP-085 is zero. The IMP-086 scorecard
SHA-256 is
`9F549FC45543C7D3F7A6E7E75A53DDBD8E4D96680C4D5E5F925C80DD34E4BB8A`.
