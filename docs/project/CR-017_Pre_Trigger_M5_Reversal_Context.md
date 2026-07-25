# CR-017 Pre-Trigger M5 Reversal Context

Version: 1.2.0

Date: 2026-07-22

Status: Rejected at real-tick smoke gate; NO-GO

Architecture Baseline: ABR-1.0

Related: CR-013, CR-015, CR-016, ADR-006, IMP-068, IMP-069, IMP-077

## Approval and purpose

The project owner approved CR-017 on 2026-07-22 after CR-016 was rejected at
its real-tick smoke gate. CR-016 delayed Entry until a later continuation close
and all 12 surviving confirmations then failed structural geometry or the
unchanged cost-aware minimum `2.0R`. CR-017 tests one causal correction: retain
Entry at the sweep/reclaim trigger close while using only a preceding completed
M5 bar as reversal context.

## Frozen candidate rule

At each completed M15 observation use exactly two completed M5 bars:

1. the penultimate M5 bar is the context bar;
2. the latest completed M5 bar is the trigger bar and retains the approved POI,
   sweep, directional candle, and minimum `0.10 ATR` reclaim contract;
3. BUY context requires a bearish context candle and a bullish trigger whose
   close is strictly above the context open;
4. SELL context is symmetric: a bullish context candle and a bearish trigger
   whose close is strictly below the context open;
5. Entry is the trigger close, never a later price;
6. Stop remains the trigger extreme plus the unchanged buffer;
7. Target remains the nearest opposing confirmed swing;
8. the unchanged cost-aware minimum `2.0R` planner remains final.

This is a two-candle body-engulfing reversal condition at the existing
sweep/reclaim POI. No context-body size threshold, Session filter, confidence
threshold, direction bias, Risk relaxation, alternative Target, or
outcome-derived exception may be added during this candidate test.

## Closed-bar timing

```text
M15 bar open        + 900 seconds = observation
M5 context open     + 600 seconds = observation
M5 trigger open     + 300 seconds = observation
M5 context open     + 300 seconds = M5 trigger open
M15 Trend known time                 = observation
confirmed M5 structure known time   = observation
```

Both M5 bars and all Brain/structure evidence must be known no later than the
trigger close. A forming/future bar, missing exact shift, invalid OHLC, invalid
ATR, or unavailable past-only structure fails closed.

## Protected boundaries

- canonical Feature Schema 4.0 and directional Label Schema 1.1 are unchanged;
- Brain provides market understanding only;
- Risk remains the final permission gate;
- Execution receives only a Risk-approved structural plan;
- Stop buffer, Target source, minimum RR, loss limits, and paper lifecycle are
  unchanged;
- provider remains Strategy-Tester-only and deployment-locked;
- broker orders, live execution, Demo attachment, Forward, and Deployment are
  forbidden;
- frozen Validation and Test evidence remain opaque and unopened.

## Evidence gates

Implementation must pass symmetric BUY/SELL acceptance, failed reversal
context rejection, exact closed-bar timing rejection, unchanged reclaim/RR
tests, dependency audit, Python regression, and MetaEditor compilation with
`0 errors / 0 warnings`.

The first evidence run is the same bounded XAUUSD M15 real-tick smoke interval
used for CR-016: 2021-06-01 through the exclusive tester end 2021-06-30. It
must preserve every Safety Lock, pass real-tick quality audit, and produce at
least one valid structural plan before any longer Train-only run is considered.
The smoke result cannot authorize Ranking, Training, Forward, Runtime
promotion, Validation/Test access, or Deployment.

## Rollback

If implementation validation or the real-tick smoke gate fails, preserve the
evidence and retire the candidate. Risk, Execution, broker state, canonical
features, labels, and sealed partitions require no rollback because CR-017 may
not modify them.

## Implementation validation

The isolated implementation completed on 2026-07-22. Setup Audit Schema 3.0
and preserved V1/V2 compatibility passed the focused offline test. The complete
Python regression passed 44/44. Stage C synchronized changed files with
matching SHA-256 and compiled 10/10 targets; the canonical Shadow compile
passed 13/13 targets. Both MetaEditor runs reported `0 errors, 0 warnings`.
No `core/risk` or `core/execution` file changed and the changed CR-017 source
contains no exact broker-mutation token. This validates implementation and
Safety boundaries only; the pre-registered real-tick smoke result is still
required and every Forward/Deployment lock remains active.

## Real-tick smoke result

The frozen candidate ran on XAUUSD M15 with `Every tick based on real ticks`
from 2021-06-01 through the exclusive tester end 2021-06-30. The run completed
on 2026-07-22 with 4,177,282 ticks and 1,932 generated bars. A run-bounded log
scan from host time 18:44:20 through 18:48:11 found no real-tick absent,
discarded, mismatch, or whole-day warning. Broker state remained unchanged,
Safety was valid, Deployment authorization was false, and the permanent
tester-only NO-GO identity was preserved.

Setup Audit Schema 3.0 produced this fail-closed funnel:

```text
1,911 observations
  -> 103 confirmed POIs
  -> 11 sweep/reclaim triggers
  -> 3 reversal-context confirmations
  -> 0 valid structural plans
```

All three reversal-confirmed observations failed the unchanged cost-aware
minimum `2.0R`. Their calculated plan RR values were approximately `0.7943R`,
`0.7696R`, and `0.7273R`. No Decision became actionable, Risk correctly
rejected all 1,911 HOLD Decisions, and Shadow Execution performed zero
executions. The Setup Outcome Dataset builder then refused the evidence with
`Objective audit contains no valid structural plans`.

CR-017 therefore failed its pre-registered requirement to produce at least one
valid structural plan and is rejected at the smoke gate. No longer-period run,
Ranking, Training, Forward, Runtime promotion, or Deployment is authorized.
Minimum RR, structural Target, Risk, and Safety Locks must not be relaxed to
manufacture coverage. Evidence is retained under
`training/output/cr017_smoke_20210601_20210630`.
