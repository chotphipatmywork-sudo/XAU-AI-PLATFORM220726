# IMP-068 Objective M15/M5 Setup Adapter

Version: 1.1.0

Date: 2026-07-18

Status: V1 validated; minimum-reclaim amendment approved

Related: CR-013, ADR-006, IMP-066, CR-012, IMP-067

## Purpose

Implement CR-013 Stage B as a deterministic, testable bridge from existing
closed-bar Brain/structure evidence into the Stage A Hybrid Setup Context.
This stage answers whether a directional idea is at an objective location with
a completed trigger and defensible structural Stop/Target.

## Contracts

- `CObjectiveMultiTimeframeSetupInput` owns explicit M15/M5 timestamps,
  existing Brain Trend and confirmed-swing results, M5 OHLC/ATR, point, costs,
  and minimum RR.
- `CObjectiveHybridSetupConfig` freezes V1 thresholds and buffer fractions.
- `CObjectiveMultiTimeframeSetupEvidence` records direction, POI, trigger,
  sweep/reclaim measurements, Stop/Target, validity, and audit reason.
- `CObjectiveMultiTimeframeSetupAdapter` validates time/data and projects the
  existing `CHybridRuleSetupContext` without accepting or approving Risk.

## Closed-bar contract

The observation is valid only when:

```text
M15 bar open + 900 seconds = observation time
M5 bar open  + 300 seconds = observation time
M15 Trend known time       = observation time
M5 structure known time   <= observation time
```

Future-known structure, forming bars, missing ATR, invalid OHLC geometry, and
invalid price/cost inputs are rejected. The adapter never loads market history,
so Stage C must later prove its source mapping separately.

## Objective V1 setup

M15 direction uses the existing Trend result and requires Regime, Momentum,
and Slope to agree at 55/45. M5 uses the latest confirmed swing as a retest POI.
BUY requires a completed low sweep and bullish reclaim; SELL is symmetric.

```text
zone tolerance    = max(10 * point, 0.10 * ATR_M5)
sweep penetration = max(1 * point, 0.02 * ATR_M5)
minimum reclaim   = 0.10 * ATR_M5
stop buffer       = max(0.10 * ATR_M5, estimated_cost_points * point)
```

IMP-073 later found that plans below the `0.10 ATR` reclaim boundary were
consistently harmful in all four frozen Train folds. The owner approved this
single symmetric BUY/SELL threshold on 2026-07-19. A weaker completed reclaim
is a valid observation but remains non-actionable.

The sweep extreme plus buffer defines structural invalidation. The nearest
opposing confirmed swing defines Target. Stage A and the existing planner then
apply confluence and cost-adjusted minimum-RR validation.

## Protected boundaries

- Feature Schema 4.0 and Label Schema 1.1.0 are unchanged.
- No H1/M1, model training, confidence target, Risk state, account state,
  Execution, or broker API enters Stage B.
- A valid adapter output is not Risk approval.
- Forward and Strategy Tester Runtime behavior remain unchanged.
- Stage C integration requires a separate review and evidence gate.

## Required validation

- synthetic BUY and SELL sweep/reclaim setups;
- higher structural RR preserved above fixed 2R;
- non-trigger observations remain non-actionable;
- sub-`0.10 ATR` reclaim observations remain non-actionable;
- forming M5/M15 bars and future-known structure are rejected;
- insufficient nearest-target RR is rejected by the existing planner;
- include closure contains no broker-capable file or mutation token;
- focused MetaEditor compile reports `0 errors / 0 warnings`.

## Workspace validation

Completed on 2026-07-18:

- four new `.mqh` files each contain exactly one primary class;
- focused include closure contains 12 files with 0 missing local includes;
- focused closure contains 0 market-loading or broker-mutation token hits;
- canonical Shadow closure remains 108 files with 0 broker-capable files and
  0 broker-mutation token hits;
- sync and compile PowerShell scripts parse successfully (2/2);
- all existing Python regression tests pass (33/33);
- synthetic arithmetic preserves BUY RR 26.121212 and SELL RR 33.696970, while
  rejecting the 1.878788 insufficient-RR case.

Operator evidence received on 2026-07-18:

- Stage B files synchronized successfully to the MT5 project copy;
- `tests\TestObjectiveMultiTimeframeSetupAdapter.mq5` compiled successfully;
- MetaEditor result: 1/1 target, 0 errors, 0 warnings.
- focused runtime execution on XAUUSD M15 passed all eight contracts;
- BUY, SELL, sweep/reclaim evidence, non-trigger handling, future/forming-bar
  rejection, insufficient-RR rejection, and the Risk boundary all reported
  `true`;
- the complete Objective M15/M5 Setup adapter contract reported `true` and the
  focused EA removed itself normally with `ExpertRemove()`.

## Closure

CR-013 Stage B is closed. The adapter remains disconnected from the canonical
Runtime, Strategy Tester provider selection, Risk, Execution, Forward, and
broker mutation. Stage C requires explicit approval and a separate integration
gate before a structure-aware Trade Plan can affect Shadow paper execution.

## CR-016 research amendment

CR-016/IMP-077 later added one tester-only two-bar M5 continuation candidate.
The penultimate completed M5 bar retains this document's sweep/reclaim rules;
the most recent completed M5 bar must hold the reclaimed POI and close farther
in the same direction. This is a new research candidate, not a retrospective
change to the accepted V1 evidence or an authorization for deployment. Its
2021-06 real-tick smoke run reached zero valid structural plans, so CR-016 was
rejected before long-period evidence, Ranking, Training, or Forward.

## Compile correction record

The first focused MetaEditor attempt exposed two MQL5 language constraints:
`input` is a reserved keyword and the original Evidence include guard exceeded
the compiler identifier-length limit. Parameter names were changed to `source`
and all four new include guards were shortened. No setup, timing, RR, Risk, or
Execution behavior changed. The corrected focused recompile passed with
0 errors and 0 warnings.

## CR-017 research amendment

After CR-016 failed its smoke gate, CR-017/IMP-078 restored Entry to the latest
completed M5 sweep/reclaim trigger close. The preceding completed M5 bar is now
causal reversal context only: BUY requires a bearish context body engulfed by
the bullish trigger close, and SELL is symmetric. POI, minimum reclaim, Stop,
Target, minimum RR, Risk ownership, and NO-GO locks remain unchanged.
Its 2021-06 real-tick smoke run produced three reversal-confirmed observations,
all below `0.80R`, and zero valid structural plans. CR-017 was therefore
rejected before any longer-period run or downstream stage.
