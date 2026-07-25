# IMP-078 CR-017 Pre-Trigger Reversal Context

Version: 1.2.0

Date: 2026-07-22

Status: Implementation valid; candidate rejected at real-tick smoke gate

Architecture Baseline: ABR-1.0

Related: CR-017, CR-016, CR-013, ADR-006, IMP-068, IMP-069, IMP-077

## Purpose

Implement the single approved CR-017 tester-only candidate without changing
Risk or Execution ownership. The latest completed M5 bar again owns the
sweep/reclaim trigger and Entry price. The immediately preceding completed M5
bar supplies only causal reversal context.

## Implementation

- `CObjectiveMultiTimeframeSetupInput` carries exact context and trigger M5
  timestamps/OHLC;
- `CObjectiveMultiTimeframeSetupEvidence` records trigger confirmation,
  reversal-context confirmation, and trigger body engulfment in ATR units;
- `CObjectiveMultiTimeframeSetupAdapter` applies the frozen symmetric
  body-engulfing reversal rule after the unchanged POI/sweep/`0.10 ATR`
  reclaim check;
- Entry is the trigger close, Stop is the trigger extreme plus the unchanged
  buffer, and Target remains the nearest opposing confirmed swing;
- `CRuntimeManager` loads M5 shifts 2 and 1 exactly and obtains Brain ATR and
  confirmed swing structure at the trigger-close observation boundary;
- `CObjectiveSetupAuditLogger` writes Setup Audit Schema 3.0;
- the offline outcome builder preserves Schema 1.0/2.0 compatibility, accepts
  exact Schema 3.0, and refuses a V3 plan that bypasses either trigger or
  reversal-context confirmation.

## Protected flow

```text
Closed M15 Brain + completed M5 context + completed M5 trigger
  -> Objective tester-only provider
  -> Decision + structural plan
  -> Risk final permission gate
  -> Shadow Execution only when Risk allows
```

No canonical feature, label, confidence threshold, Session rule, Risk
exception, Execution path, broker mutation, Forward permission, or Deployment
permission was added.

## Validation contract

- symmetric BUY and SELL reversal-context plans accepted;
- valid trigger with wrong-direction context rejected;
- sub-`0.10 ATR` reclaim rejected;
- incomplete trigger rejected;
- future/forming timing rejected;
- sub-minimum structural RR rejected;
- Risk boundary and tester-only NO-GO identity preserved;
- Setup Audit V1, V2, and V3 parsing remains fail closed;
- changed MT5 files must synchronize with matching SHA-256;
- focused and canonical MetaEditor compiles must report
  `0 errors, 0 warnings`;
- the complete offline Python regression must remain green.

## Remaining evidence gate

After implementation validation, run only the pre-registered 2021-06 XAUUSD
M15 real-tick Shadow smoke interval. It must pass tick-quality and Safety
checks and produce at least one valid structural plan before a longer
Train-only run can be considered. Ranking, Training, Validation/Test access,
Forward, Runtime promotion, Deployment, and live execution remain forbidden.

## Implementation evidence

- focused Setup Audit V1/V2/V3 parser test passed;
- complete Python regression passed 44/44;
- Stage C synchronized every changed MT5 file with matching SHA-256;
- Stage C compiled 10/10 targets with `0 errors, 0 warnings`;
- canonical Shadow Runtime compiled 13/13 targets with
  `0 errors, 0 warnings`;
- changed Risk/Execution files: zero;
- exact broker-mutation token matches in changed CR-017 source/tests: zero;
- provider identity remains `OBJECTIVE_M15_M5_SETUP_TESTER_ONLY`;
- model status remains `OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO` and
  deployment authorization remains false.

## Real-tick smoke evidence

The pre-registered 2021-06 XAUUSD M15 real-tick smoke run passed source-quality
and Safety checks but failed strategy coverage. Audit V3 recorded 1,911
observations, 103 confirmed POIs, 11 triggers, three reversal-context
confirmations, and zero valid structural plans. The three surviving candidate
plans produced only `0.7943R`, `0.7696R`, and `0.7273R` against the unchanged
minimum `2.0R`; the planner correctly rejected all three before Risk
permission. The Dataset builder correctly failed closed because no valid plan
existed.

This confirms that restoring Entry to the trigger close removed the CR-016
one-bar delay but did not provide sufficient room to the nearest opposing M5
swing in the bounded smoke interval. CR-017 is retired as a candidate. No
longer-period evidence run or downstream research stage is permitted for it.
