# IMP-069 Objective Setup Strategy Tester Integration

Version: 1.4.0

Date: 2026-07-18

Status: Stage C operational validation complete; Objective V1 quality NO-GO

Related: CR-013, ADR-003, ADR-005, ADR-006, IMP-059, IMP-060, IMP-066,
IMP-067, IMP-068

## Purpose

Connect the validated objective M15/M5 Setup and structure-aware Trade Plan to
the canonical Shadow pipeline in Strategy Tester without changing Forward,
Risk ownership, or broker state.

## Approved path

```text
Closed M15 Brain context
        +
Aligned closed M5 Brain ATR/OHLC + confirmed swing structure
        |
        v
Objective Setup provider (Tester only)
        |
        v
AI Decision + structural Trade Plan
        |
        v
Decision Intent -> Risk Gate
                       |
                       v only when Risk AllowTrade=true
              Execution price-plan adapter
                       |
                       v
              Shadow paper execution only
```

## Source timing

- canonical Runtime timeframe must be M15;
- `observation = completed M15 bar open + 900 seconds`;
- `M5 trigger open = observation - 300 seconds`;
- the M5 trigger shift must resolve exactly and be at least shift 1;
- confirmed swing loading starts at that M5 shift and moves only backward;
- M15 Trend known time and M5 structure known time equal the observation;
- no open/future M5 bar enters the source arrays.

CR-016/IMP-077 changes only the tester-only candidate mapping: M5 shift 2 is
the sweep/reclaim trigger and M5 shift 1 is the continuation confirmation. Both
must be exact completed bars. The structural entry becomes the confirmation
close; the original trigger extreme, Stop buffer, opposing-swing Target, Risk
gate, and Shadow Execution boundary remain unchanged. The 2021-06 real-tick
smoke run produced zero valid structural plans and rejected this candidate;
this mapping remains research evidence only and may not proceed to a longer
run, Ranking, Training, Forward, or deployment.

CR-017/IMP-078 supersedes that rejected tester-only candidate mapping. M5 shift
2 is causal context, M5 shift 1 is the sweep/reclaim trigger, and Entry is the
trigger close. Confirmed swing structure and all input evidence are bounded by
the trigger-close observation. Risk and Shadow Execution boundaries are
unchanged, and the replacement remains permanently deployment-locked.
The bounded real-tick smoke run later reached zero valid plans because all
three reversal-confirmed observations were below minimum RR; CR-017 is retired
and cannot proceed to a longer run, Ranking, Training, Forward, or Deployment.

## Execution contract

The Execution-owned price plan contains direction, reference Entry, absolute
Stop, absolute Target, estimated costs, minimum RR, and a validity flag. Runtime
maps the accepted AI plan into this contract. Risk receives the Decision before
the price plan can reach Shadow Execution.

At simulated entry, Shadow Execution must recheck:

- Risk is valid and explicitly allows trading;
- Decision direction matches the price plan;
- BUY has `Stop < simulated entry < Target`;
- SELL has `Target < simulated entry < Stop`;
- cost-adjusted reward and risk are positive;
- cost-adjusted RR still meets the plan minimum.

Execution applies the supplied absolute Stop/Target unchanged. Existing
providers continue to use fixed configured Shadow distances.

## Safety locks

- Objective provider is rejected outside Strategy Tester.
- Model deployment authorization remains false.
- Live execution authorization remains false.
- Broker order/position counts must remain unchanged.
- Objective audit, Decision audit, Execution audit, state, telemetry, and report
  files are isolated from all existing providers.
- Feature Schema 4.0 and Label Schema 1.1.0 are unchanged.
- No Dataset, Validation, or Test partition is read.

## Required validation

- objective provider BUY/HOLD/SELL and identity/NO-GO contracts;
- closed M15/M5 source timing and past-only swing loading;
- rejected Risk cannot open a structural paper trade;
- approved structural Stop/Target is preserved exactly;
- direction, geometry, and sub-minimum RR failures are rejected;
- duplicate, emergency-stop, and unchanged-broker-state protections pass;
- existing Shadow tests and Python regression remain green;
- focused and canonical MetaEditor targets compile with 0 errors and 0 warnings;
- same-period Strategy Tester report remains safety-valid before any quality
  comparison is interpreted.

## Workspace implementation evidence

The Stage C workspace implementation now includes:

- a Tester-only Objective inference-provider mode and permanent NO-GO status;
- exact closed M15 and aligned closed M5 source construction through Brain;
- a separate Execution-owned absolute price-plan contract;
- post-Risk structural paper-execution mapping and conservative RR recheck;
- isolated Objective audit and backtest artifacts;
- focused provider, source-timing, and structural-execution safety tests;
- SHA-256 verified synchronization and ten-target MetaEditor compile tooling.

Local validation on 2026-07-18 passed the complete 33/33 Python regression,
PowerShell parsing for the Stage C and canonical Shadow sync/compile tools, and
the canonical no-broker include-closure audit. MetaEditor compilation and the
three focused XAUUSD M15 chart tests remain required before Stage C can be
declared validated or a same-period backtest can begin.

On 2026-07-19 the Stage C synchronization/compile runner passed all ten targets
with 0 errors and 0 warnings. The ten workspace compile logs independently
confirm the same result. Three focused XAUUSD M15 chart tests remain required
before the same-period Objective Strategy Tester benchmark is authorized.

The three focused XAUUSD M15 chart tests passed on 2026-07-19. Provider
BUY/HOLD/SELL behavior, Forward/NO-GO locks, exact closed M15/M5 alignment,
future-timing rejection, unchanged Risk ownership, structural Stop/Target
preservation, RR rejection, duplicate protection, emergency stop, paper
lifecycle, and unchanged broker state all reported `true`. The same-period
Objective Strategy Tester safety benchmark is now the remaining Stage C gate.

## Accepted same-period Strategy Tester evidence

The registered XAUUSD M15 real-tick run completed on 2026-07-19 over the same
2026-06-01 through 2026-06-29 observation interval as the accepted Legacy,
Directional, and Simple Baseline comparisons.

- Decisions: 1,895; Risk rejections: 1,889; executions: 6.
- closed / winning / losing / breakeven: 6 / 0 / 6 / 0.
- cumulative result / maximum drawdown: -3,272 / 3,272 points.
- broker state unchanged, report writing, count consistency, and internal
  safety: all valid.
- provider identity: `OBJECTIVE_M15_M5_SETUP_TESTER_ONLY`.
- model status: `OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO`.
- model and live deployment authorization: false / false.

The isolated Objective Setup audit contains 1,895 rows. It records 129
POI-confirmed observations, 29 trigger-confirmed observations, and 12 valid
structural plans after minimum-RR validation. Six plans executed before the
drawdown gate halted further entries; the remaining six valid plans were
correctly rejected by Risk. Accepted plans were directionally imbalanced at
9 SELL and 3 BUY, with planned RR from approximately 2.12 to 6.12.

A read-only M15-bar path diagnostic of all twelve plans found ten Stop-first
outcomes, one Target-first outcome, and one same-bar ambiguous outcome. This is
diagnostic evidence only because M15 OHLC cannot resolve intrabar ordering.
The exact tick-backed result for the six executed plans is definitive: every
one closed at Stop Loss.

Stage C therefore passes its architecture, timing, Risk-boundary, execution,
audit, and broker-safety objectives, but Objective Setup V1 fails strategy
quality and remains NO-GO. It is not eligible for Forward, Demo attachment,
model deployment, broker orders, or live execution.

## Rollback

Remove the Objective provider mode, source/provider/price-plan contracts,
objective audit logger, focused Stage C tests, and Stage C branches. Existing
Legacy, Directional, Simple Baseline, fixed Shadow execution, Risk, and Forward
defaults require no restoration.
