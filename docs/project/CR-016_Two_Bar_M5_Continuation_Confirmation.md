# CR-016 Two-Bar M5 Continuation Confirmation

Version: 1.1.0

Date: 2026-07-22

Status: Rejected at real-tick smoke gate; NO-GO

Architecture Baseline: ABR-1.0

Related: CR-013, CR-015, ADR-006, IMP-068, IMP-069, IMP-074, IMP-076

## Purpose

Test one pre-registered entry-quality correction after the `0.10 ATR` reclaim
contract reached sufficient Train size but retained negative mean cost-aware
return and failed three of four purged folds. In the augmented Train evidence,
98 of 174 Stop-first plans reached Stop during the first later M15 bar. This is
motivation only; it does not authorize tuning against those outcomes.

## Frozen candidate rule

At each completed M15 observation, use exactly two completed M5 bars:

1. the penultimate M5 bar is the trigger bar and must satisfy the unchanged
   POI, sweep, directional candle, and `0.10 ATR` reclaim contract;
2. the most recent completed M5 bar is the confirmation bar;
3. BUY confirmation requires a bullish confirmation candle, confirmation
   close strictly above trigger close, and confirmation low strictly above the
   reclaimed swing-low POI;
4. SELL confirmation is symmetric: bearish candle, close strictly below
   trigger close, and high strictly below the reclaimed swing-high POI;
5. Entry is the confirmation close;
6. structural Stop remains the trigger extreme plus the unchanged buffer;
7. Target remains the nearest opposing confirmed swing and the existing
   cost-aware minimum `2.0R` planner remains final.

No extension threshold, Session filter, confidence threshold, direction bias,
Risk relaxation, or outcome-derived exception may be added in this change.

## Closed-bar timing

```text
M15 bar open       + 900 seconds = observation
M5 trigger open    + 600 seconds = observation
M5 confirmation open + 300 seconds = observation
M15 Trend known time                = observation
confirmed M5 structure known time  = trigger close / confirmation open
```

Both M5 bars must be closed and exact. Forming/future bars, missing shifts,
invalid OHLC, invalid ATR, or unavailable past-only structure fail closed.

## Protected boundaries

- canonical Feature Schema 4.0 and directional Label Schema 1.1 are unchanged;
- Brain still provides market understanding only;
- Risk remains the final permission gate;
- Execution still receives only a Risk-approved structural plan;
- Stop buffer, Target source, minimum RR, loss limits, and paper lifecycle are
  unchanged;
- provider remains Strategy-Tester-only and permanently deployment-locked;
- broker orders, live execution, Demo attachment, and Forward are forbidden;
- frozen Validation and Test evidence must not be opened.

## Evidence gate

Implementation requires focused symmetric BUY/SELL acceptance, missing or
failed confirmation rejection, exact closed-bar timing rejection, unchanged
minimum reclaim and RR tests, dependency audit, and MetaEditor compilation with
`0 errors / 0 warnings`. Only then may a new real-tick Train-period Shadow run
be requested. Passing a backtest cannot self-authorize Runtime promotion,
Forward, Validation/Test access, or deployment.

## Rollback

Restore the one-bar Objective input/adapter/source mapping and its audit schema.
Risk, Execution, broker state, and non-Objective inference providers require no
rollback because CR-016 may not modify them.

## Implementation validation

The isolated implementation completed on 2026-07-22. Setup Audit V2 and its V1
compatibility test passed, the complete offline Python regression passed 44/44,
the Stage C compile passed 10/10 targets, and the canonical Shadow compile
passed 13/13 targets. Both MetaEditor runs reported `0 errors, 0 warnings`.
This validates implementation and safety only; strategy evidence is still
absent and every deployment/Forward lock remains active.

## Real-tick smoke result

The frozen candidate was run on XAUUSD M15 with `Every tick based on real
ticks` from 2021-06-01 through the exclusive tester end 2021-06-30. The run
completed on 2026-07-22 with 4,177,282 ticks and 1,932 generated bars. A
run-bounded scan from host time 17:22:13 through 17:28:04 found no real-tick
absent, discarded, mismatch, or whole-day warning. The safety result remained
valid: broker state was unchanged, deployment authorization was false, and the
tester-only NO-GO provider identity was preserved.

Setup Audit Schema 2.0 produced the following fail-closed funnel:

```text
1,911 observations
  -> 121 confirmed POIs
  -> 28 sweep/reclaim triggers
  -> 12 two-bar continuation confirmations
  -> 0 valid structural plans
```

All 12 continuation-confirmed observations failed before Risk permission: six
had invalid Stop/Target geometry and six had nearest structural Target reward
below the unchanged cost-aware minimum `2.0R`. Consequently every Decision was
HOLD, Risk correctly rejected all 1,911 non-actionable Decisions, and Shadow
Execution performed zero executions. The Setup Outcome Dataset builder also
refused the evidence with `Objective audit contains no valid structural plans`.

CR-016 is therefore rejected at its smoke gate. A longer backtest, Ranking,
Training, Forward test, Runtime promotion, or deployment is not authorized.
The minimum RR, structural Target, Risk gate, and Safety Locks must not be
relaxed to manufacture coverage. The retained ignored evidence directory is
`training/output/cr016_smoke_20210601_20210630`.
