# IMP-071 Setup V2 Train-only Hypothesis Diagnostic

Version: 1.0.0

Date: 2026-07-19

Status: Implemented and executed; Stage 1 NO-GO for directional promotion

Architecture Baseline: ABR-1.0

Related: CR-014, CR-013, ADR-006, IMP-070

## Purpose and boundary

This implementation evaluates fixed CR-014 questions without fitting a model
or changing MQL5 Runtime. Its only input is the existing Stage D Train
partition. Validation and Test are not command-line inputs and remain sealed.

The diagnostic preserves Feature Schema 4.0 and uses only the canonical Trend,
Volatility, Liquidity, and Session groups. It does not consume Trade Plan
prices, RR, MFE/MAE, realized R, Risk, or Execution as predicates. Outcome is
used only as the completed Target/non-Target diagnostic response.

## Fixed calculations

Bullish 0..100 Trend and Liquidity Sweep scores are projected into plan
direction. A BUY retains the raw score; a SELL uses `100 - score`. Liquidity
range location is projected so low-range BUY observations and high-range SELL
observations receive the higher favorable-location value.

Fifteen fixed questions cover:

- directional Trend minimum, coherence, and component disagreement;
- aligned/opposed completed-bar Liquidity sweep and range location;
- Liquidity activity, Volatility regime/change;
- Session identity and early/late Session progress.

Thresholds are registered in source and are never fitted from outcome. Every
question is measured on the same four expanding, outcome-known-time-purged
folds used by IMP-070.

## Stability gate

A stable Train-only association requires all of the following:

- at least three matched observations in every one of four folds;
- at least 20 matched observations across the aggregate evaluation rows;
- a non-zero Target-rate lift with the same sign in all four folds;
- at least 5 percentage points absolute aggregate Target-rate lift.

Only a non-exploratory question whose observed sign also matches its
preregistered expected effect may become eligible to request a Stage 2
contract. Eligibility is not authorization. Stage 2, Runtime, deployment, and
broker trading remain false in every diagnostic artifact.

## Registered five-year result

The diagnostic used only the 229-row Stage D Train partition. The four fold
evaluation windows contained 115 plans with a 26.09% Target rate.

No preregistered directional question passed the complete gate:

- stronger/coherent Trend did not retain a positive lift across time;
- Trend component disagreement did not retain the expected negative lift;
- aligned/opposed Liquidity sweep evidence lacked stability or support;
- favorable/unfavorable Liquidity range location changed sign between folds.

Two exploratory Session associations were stable:

- `session_early_phase`: 41 plans, 39.02% Target rate, +12.94 percentage-point
  aggregate lift; fold support 9/15/10/7 and positive lift in 4/4 folds;
- `session_late_phase`: 35 plans, 11.43% Target rate, -14.66 percentage-point
  aggregate lift; fold support 7/7/7/14 and negative lift in 4/4 folds.

Because their expected direction was not preregistered, these findings are new
hypotheses rather than approved filters. Reclassifying them on the same data
would be leakage by selection. They require confirmation on a new untouched
later period before any Stage 2 request.

## Files and validation

- `training/diagnose_setup_v2_hypotheses.py`
- `training/test_setup_v2_hypothesis_diagnostic.py`
- `tools/run_setup_v2_hypothesis_diagnostic.ps1`
- output `research/cr014_stage1/setup_v2_hypothesis_diagnostic.json`

The focused Python test verifies BUY/SELL symmetry, readiness refusal, four
purged folds, stable positive/negative synthetic associations, sealed-partition
flags, and permanent NO-GO locks. No MQL5 source changed, so MetaEditor compile
is not applicable to IMP-071.

## Known limitation and next gate

Stage D contains only 229 Train plans, and fold-level subgroups are small. The
result does not provide a valid reversal entry, independent reversal geometry,
or causal evidence. The next valid action is to preregister the early/late
Session hypotheses and collect a new untouched real-tick period. Existing
Validation and Test must remain unopened.

The current source evidence ends at `2026.06.26 21:30`. A confirmation Dataset
must begin strictly after this boundary and must not be concatenated with the
existing Validation or Test partitions.
