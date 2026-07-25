# CR-015 Pre-Train History Augmentation

Version: 1.1.0

Date: 2026-07-22

Status: Completed; stable Train-only gate failed; Runtime and deployment NO-GO

Architecture Baseline: ABR-1.0

Related: CR-013, CR-014, IMP-070, IMP-074, IMP-075

## Purpose

Increase the Objective Setup development sample without weakening the frozen
200-record Train gate, opening sealed Validation/Test evidence, reusing the
post-cutoff confirmation period, or fitting thresholds to outcomes. The only
permitted source is canonical real-tick replay strictly earlier than the
existing Train evidence.

## Frozen existing evidence

- existing Train observations: `2021.07.06 11:45` through
  `2025.07.15 09:30`, 182 records;
- Validation starts `2025.07.16 03:00` and remains sealed at SHA-256
  `0A741F1D8202DA749F5D94C4045C10BFE7C8EEEF9E7096FE81B9B32CECB7F683`;
- Test starts `2026.01.19 09:30` and remains sealed at SHA-256
  `8F5C596352946A5A13B82A5BB172A29B6852791FBF8B81614FB255912E57A446`;
- post-`2026.06.26 21:30` evidence remains reserved for CR-014 confirmation
  and is forbidden as development evidence.

## Authorized source interval

Collect XAUUSD M15 history with the canonical Objective M15/M5 tester-only
provider from `2020.01.01 00:00` through `2021.06.30 23:59`. Every feature must
come from replayed Brain output under Feature Schema 4.0. Labels and outcomes
retain the approved completed-bar contracts; no second feature or label
definition is permitted.

The collected interval may be shortened only when the broker has no earlier
real-tick coverage. It may never extend into or overlap the existing Train,
Validation, Test, or CR-014 confirmation evidence.

## Fail-closed augmentation contract

- archive raw Tester artifacts and SHA-256 hashes before analysis;
- audit every MT5 real-tick quality warning and quarantine affected dates;
- construct Setup outcomes with the existing `0.10 ATR` reclaim and minimum
  `2.0R` contracts;
- quarantine ambiguous outcomes and keep outcome fields out of predicates;
- prepend eligible mature outcomes to the existing Train partition only;
- preserve chronological and outcome-known-time ordering;
- do not regenerate or resplit Validation/Test;
- verify the frozen Validation/Test hashes before and after augmentation;
- retain the 200-record Train, 40 Target, and 40 non-Target minimums;
- keep Risk, Execution, Runtime, Forward behavior, and public contracts
  unchanged.

## Exit gate

If augmented Train does not meet every frozen readiness gate, ranking remains
blocked. If it does, only the already registered Train-only ranking and purged
walk-forward process may run. Passing Train ranking is evidence to request a
later review; it does not authorize Validation/Test access, Runtime changes,
Forward Shadow, deployment, broker orders, or live execution.

## Collected source and quality gate

The canonical XAUUSD M15 real-tick replay completed on 2026-07-22 for
`2020.01.01` through `2021.06.30`. It retained broker state, wrote its report,
returned `OnTester result 1`, kept the Objective model at
`OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO`, and authorized no deployment. The
paper lifecycle recorded 18 closed plans, all 18 reaching Stop before Target;
this is evidence collection, not a promotion result.

MT5 reported 52 distinct daily source-quality anomalies: 25 dates with absent,
discarded, or mismatched real ticks and 27 dates with no real ticks. All 52
dates are quarantined by the CR-015 versioned exclusion file. The audit parser
was extended to fail closed on MT5's `no real ticks within a day` and
`tick prices mismatch` daily message forms; aggregate range summaries remain
excluded from daily-date parsing. Dataset construction and augmentation are
forbidden until the focused audit test passes and the archived log reports
complete quarantine coverage.

After quarantine, Dataset construction retained 51 mature plans: 13
Target-first and 38 Stop-first. Nine additional structural plans were excluded
because their observation-to-outcome path touched a quarantined date. The
admissible rows increased Train from 182 to 233 records, with 59 Target and 174
non-Target outcomes, so the frozen 200/40/40 readiness gate passed. Frozen
Train, Validation, and Test hashes matched before and after augmentation;
Validation and Test were never parsed.

The added 51 records had a 25.49% Target rate and -0.1275R mean cost-aware
return. The augmented Train Target rate remained essentially unchanged at
25.32%, while mean cost-aware return moved from -0.0641R to -0.0780R. The
augmentation therefore solved only the sample-size deficiency; it did not
establish a positive strategy edge.

The registered four-fold outcome-known-time-purged ranker selected the balanced
logistic candidate. Aggregate evaluation over 117 rows produced 41.18% Target
precision, 60.00% Target recall, and 59.55% Macro F1. Only one of four folds
passed the complete gate, so the stable research gate failed and no preliminary
model artifact was written. Further model or threshold search is not authorized
from this result.

## Safety state

- offline Train-only selection performed: true;
- stable research gate passed: false;
- further model or threshold tuning authorized: false;
- setup contract change authorized: false;
- Runtime integration authorized: false;
- model deployment authorized: false;
- live execution authorized: false;
- permanent status: `NO_GO` until an explicit later promotion decision.
