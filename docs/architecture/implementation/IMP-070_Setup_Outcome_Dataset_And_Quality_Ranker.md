# IMP-070 Setup Outcome Dataset and Quality Ranker

Version: 1.5.0

Date: 2026-07-19

Status: Five-year Train-only evidence complete; stable ranker gate NO-GO

Related: CR-013, ADR-003, ADR-005, ADR-006, IMP-069

## Purpose

Build a separate offline research Dataset that asks whether an already-valid
Objective M15/M5 Setup reaches its structural Target before its structural Stop.
The ranker may later recommend accept or abstain. It cannot select direction,
change Entry/Stop/Target, approve Risk, execute, or authorize deployment.

## Ownership and isolation

- Source Setup and Trade Plan come from the Stage C Objective audit.
- Model inputs are exactly the existing twelve Feature Schema 4.0 values from
  replayed Brain output, grouped only as Trend, Volatility, Liquidity, Session.
- Raw Entry, Stop, Target, planned RR, MFE, MAE, close time, and outcome are
  audit/label fields and are forbidden model inputs.
- Label Schema 1.1.0 remains unchanged. Setup Outcome Schema 1.0.0 is a
  separate research contract and cannot replace the directional Dataset.
- Runtime, Forward, Risk, Execution, broker state, and canonical model artifacts
  are not read or modified by Stage D training tools.

## Frozen Setup Outcome V1

For every `plan_available=true` Objective audit row:

1. join exactly one Feature Schema 4.0 Decision row at the same observation;
2. inspect only later completed M15 bars beginning at the Setup observation;
3. observe at most 64 completed M15 bars;
4. for BUY, Target is hit when High reaches Target and Stop when Low reaches Stop;
5. for SELL, Target is hit when Low reaches Target and Stop when High reaches Stop;
6. first unique boundary hit defines `TARGET_FIRST` or `STOP_FIRST`;
7. neither boundary within 64 complete bars defines `TIMEOUT`;
8. both boundaries in the same M15 bar define `AMBIGUOUS` and the row is
   quarantined from model training;
9. an incomplete 64-bar path without a boundary hit defines `UNMATURED` and is
   quarantined.

The builder records outcome-known time, bars observed, MFE and MAE in points
and R. These are post-observation data and must never enter the feature matrix.

## Leakage controls

- Decision observations and Objective Setup observations must be unique and
  strictly chronological.
- The canonical Decision observation is exactly `closed M15 bar + 15 minutes`.
  On real ticks, `recorded_at` may be delayed by the first available tick, but
  must not be early or exceed the Runtime freshness limit of 120 seconds.
- Join keys must match exact symbol and observation timestamp.
- Features must be finite and within `[0,100]`.
- Plan direction and price geometry must be valid before outcome evaluation.
- Training/evaluation boundaries are time-based: every training row must have
  `outcome_known_at` earlier than the next evaluation start.
- The maximum label horizon is 64 M15 bars (16 hours); no record-count shortcut
  may replace this time rule when Setup rows are sparse.
- Candidate selection reads only the Setup Outcome Train partition. Validation,
  Test, and a later untouched period remain sealed.

## Readiness gate

Training must refuse to start unless the Train partition has:

- at least 200 mature, non-ambiguous Setup rows;
- at least 40 `TARGET_FIRST` rows;
- at least 40 non-target rows (`STOP_FIRST` plus `TIMEOUT`);
- at least four valid chronological evaluation folds;
- both binary quality classes in every evaluation fold after temporal purging.

The current one-month Stage C evidence contains only twelve valid plans and is
therefore diagnostic-only and explicitly insufficient for training.

## Ranker boundary

The first ranker compares an accept-all Setup baseline, a class-balanced
logistic model, and a bounded class-balanced random forest over expanding
Train-only folds. Selection prioritizes stable fold gates, then Target-class
precision, Macro F1, and balanced accuracy. All artifacts are research-only,
carry permanent `NO_GO`, and are forbidden from MQL5 or Runtime integration.

Promotion requires a later explicit decision after nested purged stability and
an untouched later-period evaluation. A favorable Train-only result alone can
never authorize Forward, Demo, broker orders, or live execution.

## Validation

- focused synthetic builder test for Target/Stop/Timeout/Ambiguous/Unmatured;
- exact join, feature-range, geometry, and duplicate rejection tests;
- focused readiness and time-purge tests;
- complete existing Python regression remains green;
- current twelve-plan evidence builds deterministically and training refuses it;
- expanded historical evidence is required before ranker evaluation.

## Workspace validation and first evidence

The Stage D workspace implementation contains an exact-schema outcome builder,
chronological outcome-known-time splitter, readiness-gated four-fold Train-only
ranker, three focused Python tests, and beginner-safe PowerShell operator tools.
No MQL5, Runtime, Risk, Execution, Forward, or broker file was changed.

On 2026-07-19:

- Target/Stop/Timeout/Ambiguous/Unmatured synthetic contracts passed;
- duplicate, feature-range, RR-consistency, and temporal-purge rejection passed;
- insufficient-data refusal and sealed Validation/Test boundaries passed;
- predictable synthetic Train-only ranking passed without deployment authority;
- complete Python regression passed 37/37 after adding the focused generation
  parity comparator;
- both Stage D PowerShell tools parsed successfully.

The one-month Objective evidence built deterministically from 1,895 Decision
and Setup-audit rows. It produced 12 structural plans: 10 `STOP_FIRST`, one
`TARGET_FIRST`, and one quarantined `AMBIGUOUS`, leaving 11 trainable rows.
Readiness correctly failed against requirements of 200 trainable, 40 Target,
and 40 non-Target rows. No split, fitting, or model artifact was authorized.

The next evidence step is a longer Objective Strategy Tester run using the
unchanged Stage C provider and isolated files. Dataset construction must be
repeated after the run; thresholds may not be weakened to fit available data.

Before a multi-year generation run, the same one-month interval may be rerun
with the faster `1 minute OHLC` Strategy Tester model. Exact Decision OHLC/ATR,
all twelve Feature values, and all Setup/Plan source fields must match the
preserved real-tick reference. Risk and paper-execution fields are intentionally
ignored because this parity gate authorizes Dataset generation only. If parity
fails, expanded generation must use real ticks. Final strategy-quality evidence
always returns to real ticks regardless of generation parity.

The reference real-tick Setup, Decision, and Report artifacts were preserved
with SHA-256 hashes before the rerun. The parity comparator and its focused
test pass against identical reference evidence, validating the comparator.

The same interval was then rerun with `1 minute OHLC` on 2026-07-19. All 1,895
Decision observations and their OHLC, ATR, and twelve Feature values matched
the real-tick reference exactly. The same twelve timestamps also produced
plans, and the accepted Entry, Stop, and Target prices matched. However, strict
Setup/Plan parity failed with 38 field mismatches: 14 rejected observations had
structural Stop differences of one or two points, all twelve accepted plans had
an estimated-cost difference of one point, and their cost-adjusted planned RR
therefore differed. The paper-execution result also changed from six trades to
five and remained loss-only.

This evidence rejects `1 minute OHLC` for Stage D Dataset generation. Small
spread and structural-price differences can change minimum-RR acceptance on a
different interval, so the parity contract must not be weakened merely because
the accepted plan set happened to match in this month. Expanded generation and
all final quality evidence must use `Every tick based on real ticks`.

The five-year real-tick run completed safely on 2026-07-19 with 116,688
Decision rows and all isolated artifacts written. Its first Dataset build
exposed a Builder defect rather than a Runtime defect: 6,070 valid Decisions
were recorded one to 120 seconds after the canonical M15 boundary because the
first real tick arrived late. No Decision was early or later than the frozen
120-second freshness limit. Builder validation now indexes the canonical
closed-bar observation while retaining and enforcing the actual timestamp lag.

The MT5 source audit identified sixteen dates with absent, discarded, or
mismatched real ticks. A versioned Source-Quality Exclusion file conservatively
quarantined every plan whose observation-to-outcome interval touched one of
those dates. Three of 332 plans were excluded: one Target-first and two
Stop-first plans. None belonged to the Train partition.

The final quality-controlled Dataset contains 329 plans: 70 Target-first, 257
Stop-first, and two quarantined same-bar ambiguous outcomes. Chronological
splitting produced 229 Train rows (52 Target / 177 Stop), 49 sealed Validation
rows (11 / 38), and 49 sealed Test rows (7 / 42). Outcome-known-time purging
passed without leakage.

The four-fold Train-only ranker selected the bounded class-balanced random
forest candidate, but the stable gate failed. Aggregate evaluation contained
115 samples with 38.10% Target precision, 26.67% Target recall, and 55.91%
Macro F1; only one of four folds passed. Validation and Test were not opened,
no preliminary model file was written, and deployment remains unauthorized.
Stage D evidence is therefore complete with a quality `NO_GO`, not a promoted
model.

## Rollback

Remove the Stage D offline scripts, focused Python tests, research outputs, and
this document. Stage C Runtime and all protected production boundaries require
no restoration because Stage D does not modify them.
