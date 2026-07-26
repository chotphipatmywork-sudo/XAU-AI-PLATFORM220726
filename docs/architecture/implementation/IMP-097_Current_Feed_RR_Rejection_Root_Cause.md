# IMP-097 Current-Feed RR Rejection Root Cause Analysis

Version: 1.0.0

Date: 2026-07-26

Status: Completed; structural RR distance is dominant; Runtime remains NO-GO

Architecture Baseline: ABR-1.0

Related: IMP-095, IMP-096

## Purpose and frozen contract

IMP-097 explains why the frozen `m5_stop_2 + m15_target_1` geometry is
rejected by the existing `2.0R` Minimum-RR gate. It does not change Entry,
Stop, Target, cost, gate logic, Runtime, Risk, Execution, or Deployment.

The analysis uses the same 597 Train-only current-feed requests and frozen
source hashes as IMP-095/096. Validation and Test remain sealed. Decision
context is joined at recorded decision-minute precision; Strategy Tester
seconds are normalized to the request schema minute without moving an
observation forward in time.

## Methodology

Only structurally valid, cost-known, positive cost-aware geometries enter the
Minimum-RR population. Rejections are attributed mutually exclusively to:

1. `STRUCTURAL_RAW_RR_BELOW_MINIMUM`: raw reward/risk is below `2.0R`;
2. `COST_EROSION_BELOW_MINIMUM`: raw reward/risk reaches `2.0R`, but frozen
   trading cost reduces adjusted RR below the gate.

Distances are reported in points and ATR units. Direction, Session, fixed
six-hour time blocks, Volatility regime, Trend regime, and Trend alignment
use fixed bins. Group rejection rates use Wilson 95% intervals and two-sided
proportion tests with a minimum 20 records per side and Bonferroni correction
across 17 comparisons. These are associations, not causal trading rules.

## Findings

- Requests: 597.
- Structurally valid geometry: 567.
- Valid cost-aware geometry: 459.
- Minimum-RR accepted/rejected: 76/383.
- Rejection rate: `83.44%`, Wilson 95% interval `79.77%-86.56%`.
- Raw structural RR below minimum: 310 (`80.94%` of rejections).
- Cost erosion below minimum: 73 (`19.06%` of rejections).
- Rejected Stop distance median: `132` points; accepted: `52.5` points.
- Rejected Target distance median: `113` points; accepted: `301.5` points.
- Entry distance from the recorded decision close is zero for both groups;
  Entry distance does not explain rejection in this frozen evidence.
- Rejected/accepted median frozen cost: `24/22` points. Cost contributes but
  is not the dominant cause.
- BUY/SELL rejection rates: `84.03%/82.81%`; not significant.
- No Session, Volatility, Trend, or Trend-alignment group is significant after
  correction.
- The fixed `18:00-23:59` group has `74.62%` rejection versus `86.93%` for the
  complement, Bonferroni `p=0.0235`. It is retained only as a bounded future
  research hypothesis because IMP-096 was selected after Train inspection.

## Root cause summary

The dominant failure is structural proportion: Stop distance is generally too
large relative to available structural Target distance before cost is applied.
Trading cost explains a material minority, but lowering the RR gate or changing
cost is not supported. Direction and regime segmentation do not explain the
rejection population. The single time association is insufficient to create a
filter or Candidate.

## Validation and evidence

- Focused deterministic unit test: PASS.
- Frozen source hashes: PASS.
- IMP-095 accounting parity: PASS for requests, selected Stop/Target, `2.0R`,
  valid cost-aware geometry, rejections, and accepted geometries.
- Root-cause report SHA-256:
  `403AB570A756A9C6F708BDB7B62E4A56644D138AAC675ED72FCD10E73191000C`.
- Detail record SHA-256:
  `AB32EC7B6212DBD78169DB9339B666CA3A6076381B2152D827E272AF1805B83D`.
- Validation/Test used: false/false.
- Training performed: false.
- Runtime/Risk/Execution changed: false/false/false.
- Deployment authorized: false.
- Research Scorecard: `NO_GO_TRAIN`; Research Quality `100.0`, Strategy Evidence
  `19.82`, Operational Safety `100.0`, Overall Readiness `49.0`.
- Delta Report versus the accepted reference: `0.0` for every score dimension.
- Baseline promotion allowed: false.
- Research Scorecard SHA-256:
  `97496584658A70385D149C2A9A6CA2339E8DF7319655341EDA1031727362EBBA`.

## Limitations

The frozen geometry was selected after a 49-combination Train frontier, so
IMP-097 is diagnostic rather than independent confirmation. Statistical group
results are exploratory and do not establish causality. The accepted formal
current-feed Baseline remains IMP-089 and its strategy evidence is unchanged.

## Gate decision

`NO-GO`.

No Runtime Candidate, parameter change, RR relaxation, trading filter, model,
or deployment proposal is created. The next permitted milestone is a separately
approved, preregistered Train-only investigation of why the structural Stop is
large relative to the available Target; the `18:00-23:59` association may be
included only as a fixed hypothesis with independent confirmation requirements.