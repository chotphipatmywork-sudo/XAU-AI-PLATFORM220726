# IMP-077 Two-Bar M5 Continuation Confirmation

Version: 1.1.0

Date: 2026-07-22

Status: Implementation valid; candidate rejected at real-tick smoke gate

Architecture Baseline: ABR-1.0

Related: CR-016, CR-013, ADR-006, IMP-068, IMP-069, IMP-074

## Purpose

Implement the single CR-016 tester-only candidate without changing protected
Risk or Execution ownership. The prior one-bar sweep/reclaim remains the trigger
and a second completed M5 continuation bar is now required before a structural
plan becomes actionable.

## Implementation

- `CObjectiveMultiTimeframeSetupInput` now carries exact trigger and
  confirmation M5 timestamps/OHLC;
- `CObjectiveMultiTimeframeSetupEvidence` records trigger confirmation,
  continuation confirmation, and directional confirmation extension;
- `CObjectiveMultiTimeframeSetupAdapter` preserves the POI, sweep, `0.10 ATR`
  reclaim, Stop buffer, Target, and minimum-RR rules while applying the frozen
  symmetric CR-016 continuation rule;
- `CRuntimeManager` loads M5 shifts 2 and 1 exactly, obtains ATR/structure from
  the trigger boundary, and enters only at the completed confirmation close;
- `CObjectiveSetupAuditLogger` writes Setup Audit Schema 2.0 with the second
  timestamp and confirmation evidence;
- the offline outcome builder accepts both preserved Audit V1 and new Audit V2
  files, and refuses a V2 plan that bypasses either confirmation.

## Protected flow

```text
Closed M15 Brain + closed M5 trigger + closed M5 confirmation
  -> Objective tester-only provider
  -> Decision + structural plan
  -> Risk final permission gate
  -> Shadow Execution only when Risk allows
```

No new canonical feature, label, model, confidence rule, Risk exception,
Execution path, broker mutation, Forward permission, or deployment permission
was added.

## Focused validation

- symmetric BUY and SELL two-bar plans accepted;
- sub-`0.10 ATR` trigger rejected;
- valid trigger with failed continuation rejected;
- incomplete trigger rejected;
- future/forming timing rejected;
- sub-minimum structural RR rejected;
- Risk boundary and tester-only NO-GO identity preserved;
- Setup Audit V1 and V2 offline parsing passed, including V2 bypass refusal;
- Stage C synchronization verified SHA-256 for every changed MT5 copy;
- MetaEditor compiled all 10 Stage C targets with `0 errors, 0 warnings`.
- the complete offline Python regression passed 44/44;
- the canonical Shadow compile passed all 13 targets with
  `0 errors, 0 warnings`.

## Real-tick smoke validation

The 2021-06-01 through exclusive end 2021-06-30 XAUUSD M15 real-tick run
completed successfully with broker state unchanged, safety valid, deployment
authorization false, and no run-bounded real-tick quality warning. Audit V2
recorded 1,911 observations, 121 confirmed POIs, 28 triggers, 12 continuation
confirmations, and zero valid structural plans. Of the 12 surviving
confirmations, six failed structural Stop/Target geometry and six failed the
unchanged cost-aware minimum `2.0R`.

This result validates the new audit path and fail-closed integration while
rejecting the candidate strategy. The confirmation-close entry consumed or
passed the remaining opposing-swing reward in every surviving observation.
The Dataset builder correctly stopped because no valid structural plan existed.
No longer-period run, Ranking, Training, Forward test, Runtime promotion,
deployment, or live execution is permitted for CR-016. Risk, Target selection,
minimum RR, and all Safety Locks remain unchanged.
