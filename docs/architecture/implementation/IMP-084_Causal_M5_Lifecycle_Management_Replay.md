# IMP-084 Causal M5 Lifecycle Management Replay

Version: 1.2.0

Date: 2026-07-23

Status: Completed; both management Candidates rejected; Baseline unchanged;
NO-GO

Architecture Baseline: ABR-1.0

Related: RSCS-1.0, CR-013, IMP-080, IMP-082, IMP-083

## Purpose

Test whether the favorable-excursion giveback identified by IMP-083 can be
reduced by a causal lifecycle rule. Isolate management from signal quality by
keeping Entry, initial structural Stop, structural Target, minimum `2.0R`,
position size, Risk, and all Runtime boundaries unchanged.

This stage is an offline Train replay. It cannot create a Runtime Change
Request, open Validation/Test, start Forward, execute a broker order, or
authorize Deployment.

## Frozen evidence

- augmented Train SHA-256:
  `F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E`;
- Effective Sample audit SHA-256:
  `2646BBD8E881B6BB7F8621E27D1933BE1376711C75558E046B9EA964A1393414`;
- maximum non-overlapping Effective Train sample: 232;
- path timeframe: M5 from the Setup observation through its frozen mature
  `outcome_known_at` boundary;
- exact timestamps define the authoritative mature window; the absolute path
  ceiling is 192 M5 bars (`64 M15 × 3`) because broker M15 and M5 history can
  contain different missing-bar calendars;
- missing/incomplete history, request drift, path drift, or Baseline outcome
  mismatch fails closed.

## Pre-registered candidates

1. `CURRENT_BASELINE`: initial Stop and Target remain active without additional
   management.
2. `COST_COVERED_BREAKEVEN_AFTER_CLOSE_1R`: after a completed M5 close reaches
   `+1.0` gross initial-risk R, move Stop to Entry plus/minus stressed estimated
   cost. The new Stop becomes active on the next M5 bar.
3. `TWO_STAGE_RATCHET_AFTER_CLOSE_1R_2R`: use the same cost-covered Breakeven
   after a completed `+1R` close; after a completed `+2R` close, lock `+1R` of
   gross initial risk. Each new Stop becomes active on the next M5 bar.

Activation uses M5 close, not M5 High/Low, so the management decision is known
before it becomes active. If Target and the currently active Stop occur in the
same M5 bar, that Candidate/record is `AMBIGUOUS` and quarantined. No favorable
ordering is invented.

## Frozen cost stress

Replay every Candidate with estimated transaction cost multipliers:

```text
1.00x, 1.25x, 1.50x
```

The stressed cost is included in effective initial risk, Target return, and
the cost-covered Stop. Exported historical spread is retained for audit, but
no after-the-fact cost threshold may be selected.

## Frozen Train gates

A management Candidate passes only if all are true:

- Effective N is at least 200 after M5 ambiguity quarantine;
- Mean cost-aware R is positive and moving-block 95% CI lower bound is positive;
- all four chronological blocks and both directions have positive Mean R;
- Profit Factor is at least `1.10`;
- maximum drawdown is at most `25R`;
- longest loss sequence is at most 10;
- Mean R and 95% CI lower bound remain positive at every cost multiplier.

A higher Mean R alone is insufficient. A failed Candidate remains recorded and
does not replace the IMP-083 Baseline.

## Implementation boundary

- `training/build_lifecycle_path_requests.py` creates and hashes the 232 frozen
  requests;
- `core/ai/PastOnlyLifecyclePathExporter.mqh` exports mature M5 OHLC paths and
  contains no order API;
- `tests/TestPastOnlyLifecyclePathExporter.mq5` validates window and geometry
  contracts before export;
- `training/replay_lifecycle_management.py` performs deterministic offline
  replay, cost stress, uncertainty, stability, and tail gates;
- `tools/prepare_lifecycle_path_research.ps1`,
  `tools/compile_lifecycle_path_research.ps1`, and
  `tools/collect_lifecycle_path_research.ps1` provide the repeatable workflow.

## Safety locks

- `deployment_authorized=false` in every request and export row;
- no `CTrade`, `OrderSend`, position, or broker mutation API is present;
- Validation/Test datasets are not accepted inputs;
- no Feature/Label Schema, Brain, Decision, Risk, Execution, or Trade Lifecycle
  Runtime code is modified;
- Live Execution and Deployment remain NO-GO regardless of replay result.

## Validation plan

Focused Python tests must cover request sealing, Candidate freeze, activation
on completed M5 close, next-bar effectiveness, cost-covered Breakeven,
two-stage Ratchet, cost stress, and same-M5 collision quarantine. The focused
MQL5 exporter must compile with exactly `0 errors, 0 warnings`. Complete Python
regression follows implementation. Actual results and RSCS deltas are appended
only after a hash-sealed M5 export passes Baseline parity.

## Preparation and validation result

The frozen builder produced 232 requests covering `2020.03.20 22:45` through
`2025.07.15 09:30`. The request SHA-256 is
`42FB2CA1EA960ADB902D868E06E134D95D9229DEB5B38E01BA6DD8FA19CBAD10`; the
manifest SHA-256 is
`2FE5B5E6FB9EC63796E1F230FFDE1D3539EF70C29D9FBF3B3E779A3273BDD220`.
The request copy in the active MT5 Files directory matched the Workspace hash.

The focused MQL5 exporter synchronized with SHA-256
`441749ADF7722155B59E25B17A672A9D31505CD202FC763FDC4D5D4AA956B0DD` and
the focused test synchronized with SHA-256
`7B081359682C1B03A09B83BE3EEFA6192EFE3C572BA5D311CB61A33FA71334B2`.
The test
compiled in MetaEditor with exactly `0 errors, 0 warnings`. Static inspection
found no order or position API. Both new focused Python tests passed and the
complete Python regression passed `52/52`.

At this validation stage no M5 result had been observed. Candidate definitions,
cost levels, ambiguity policy, and gates above therefore remained genuinely
pre-registered before collection.

## Request contract correction

The first collection attempt failed closed at request
`lifecycle_20210408_1830`: its source outcome contained 31 observed M15 bars,
while the broker supplied more than the derived `31 × 3 = 93` M5 bars inside
the same exact mature time window. No output Artifact survived the abort and
no Candidate result was calculated or observed.

The superseded v1.0 request SHA-256 was
`BADA9863A3162D9CD680966D23A39CA4028D6A8F9CA16156C8896F62EB13E2C2`;
the superseded manifest SHA-256 was
`934CF395390293BFDD156141856737DB5C0EE12370301ACA44C3F1DC789C2519`.

Request/manifest schema `1.1.0` therefore replaces the per-record
`bars_observed × 3` ceiling with the pre-existing absolute 192-bar safety
ceiling. `observation_time` inclusive and `outcome_known_at` exclusive remain
the causality boundary, and the exporter still verifies the first M5 open,
last M5 close, strict ordering, OHLC geometry, and every bar's membership in
that window. This correction changes evidence collection only; Candidates,
gates, costs, Entry, initial Stop/Target, Risk, Runtime, and Deployment locks
are unchanged.

## Completed collection

The v1.1 exporter completed all 232 requests and wrote 2,370 M5 path rows. The
hash-sealed export SHA-256 is
`AF4C0031F9EDEB58F4FFB7B4F86044938FA992DABD8A804AFEB7BB9090693758`.
Completeness, exact request parity, mature-window boundaries, strict sequence,
OHLC validity, protected flags, and Baseline outcome parity all passed. The
replay report SHA-256 is
`97675D0EBDF8ED85A88E6B118A9412F2513477E85DD6C84B38FFE309362D2630`.

## Train-only result

| Candidate / cost | Effective N | Target / managed / ambiguous | Mean R | 95% CI | PF | Max DD | Longest loss |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline 1.00x | 232 | 59 / 0 / 0 | -0.074 | [-0.284,+0.138] | 0.901 | 34.47R | 15 |
| Baseline 1.25x | 232 | 59 / 0 / 0 | -0.112 | [-0.313,+0.093] | 0.849 | 38.87R | 15 |
| Baseline 1.50x | 232 | 59 / 0 / 0 | -0.147 | [-0.340,+0.052] | 0.803 | 42.82R | 15 |
| Breakeven 1.00x | 232 | 42 / 59 / 0 | -0.079 | [-0.267,+0.117] | 0.861 | 28.88R | 19 |
| Breakeven 1.25x | 232 | 41 / 60 / 0 | -0.115 | [-0.293,+0.075] | 0.796 | 33.24R | 16 |
| Breakeven 1.50x | 232 | 40 / 61 / 0 | -0.153 | [-0.322,+0.029] | 0.728 | 39.03R | 10 |
| Ratchet 1.00x | 230 | 35 / 64 / 2 | -0.125 | [-0.288,+0.037] | 0.780 | 29.74R | 16 |
| Ratchet 1.25x | 230 | 34 / 65 / 2 | -0.164 | [-0.318,-0.008] | 0.713 | 37.62R | 16 |
| Ratchet 1.50x | 230 | 33 / 66 / 2 | -0.206 | [-0.350,-0.060] | 0.639 | 47.30R | 10 |

At primary 1.00x cost all three variants produced only one positive
chronological block out of four and zero positive directions out of two. Both
Candidates passed only the effective-sample gate. Positive expectancy,
temporal stability, direction robustness, Profit Factor, drawdown/tail, and
cost-stress gates failed. No Candidate is eligible for ranking or locked
Validation.

Breakeven reduced maximum drawdown at 1.00x relative to Baseline, but it also
reduced completed Targets from 59 to 42, extended the longest loss sequence
from 15 to 19, and left Mean R more negative. Ratchet reduced completed Targets
further and was materially worse under cost stress. The causal evidence rejects
both frozen management hypotheses; favorable-excursion giveback alone is not
sufficient evidence that either rule improves the strategy.

## RSCS-1.0 result

| Score | Baseline | Breakeven | Ratchet |
| --- | ---: | ---: | ---: |
| Research Quality | 100.00 | 100.00 | 100.00 |
| Strategy Evidence | 20.00 | 18.75 | 18.75 |
| Operational Safety | 100.00 | 100.00 | 100.00 |
| Raw Overall | 60.00 | 59.38 | 59.38 |
| Hard-gated Overall Readiness | 49.00 | 49.00 | 49.00 |

Candidate Strategy Evidence is 1.25 points below Baseline because both failed
the same economic/stability gates and Candidate-dependent ranker evidence was
not run after the earlier failures; unknown evidence receives zero credit.
Both Candidate scorecards are `NO_GO_TRAIN`, `baseline_promotion_allowed=false`,
and `deployment_authorized=false`.

Scorecard SHA-256 values:

- Baseline: `0CE865390FACBEC29CCA45E1136F1756C1ECE6C238CD21F41B0ACD02F22D4C11`;
- Breakeven: `3A7C610EFF3806E0C68D1B97EB6B5638E4291E3C3D226E7FAD8625C6CCA4325A`;
- Ratchet: `0F725D0261AD7C58E9B324A27395DEA9F93CC6CA37EAFD1B1FDCAACEBAB56852`.

No Runtime Change Request is created. The accepted Baseline remains unchanged,
Validation/Test remain sealed, Forward is not started, and Live Execution and
Deployment remain NO-GO.
