# CR-015 Pre-Train History Augmentation

Version: 1.0.0

Date: 2026-07-22

Status: Approved for isolated evidence collection; Runtime and deployment NO-GO

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

## Safety state

- model training authorized: false until augmented Train readiness passes;
- setup contract change authorized: false;
- Runtime integration authorized: false;
- model deployment authorized: false;
- live execution authorized: false;
- permanent status: `NO_GO` until an explicit later promotion decision.
