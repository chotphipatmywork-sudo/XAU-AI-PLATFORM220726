# IMP-066 Hybrid Rule and Structure-Aware Trade Plan

Version: 1.0.0

Date: 2026-07-18

Status: Stage A implemented, compiled, and focused MT5 contract validated

Related: CR-013, ADR-006, CR-012, IMP-065

## Purpose

Implement CR-013 Stage A contracts without changing the canonical Runtime or
the active Dataset export. This stage separates directional setup evidence from
structural price planning and from final Risk permission.

## Implementation

The internal AI Runtime research package contains:

- `CHybridRuleSetupContext`: explicit closed-bar confluence, price geometry,
  estimated cost, and minimum-RR input;
- `CTradeSetupCandidate`: accepted directional opportunity evidence;
- `CStructureAwareTradePlan`: proposed Entry, Stop, nearest structural Target,
  cost-adjusted risk/reward, and audit reason;
- `CHybridRuleSetupEngine`: rejects incomplete confluence and invalid BUY/SELL
  geometry;
- `CStructureAwareTradePlanner`: applies conservative cost adjustment and
  rejects the nearest target when it does not meet minimum RR.

No class accesses market history, Dataset files, account state, Risk state,
Execution, order APIs, or broker state.

## Adaptive RR behavior

The default minimum is 2.0R. The planner does not force Take Profit to exactly
2.0R. If the nearest verified structural Target provides 3.0R, the output keeps
that target and ratio. If the nearest target provides less than 2.0R after
estimated costs, the plan is invalid.

This is deliberately conservative: Stage A does not skip a nearer structural
obstacle to claim a more distant target.

## Boundary preservation

- the package is internal to AI Runtime ownership;
- the protected top-level path is unchanged;
- Feature Schema 4.0 and Label Schema 1.1.0 are unchanged;
- Setup Context, Setup Candidate, Trade Plan, Confidence, Risk, and Execution
  Result remain separate data concepts;
- the plan reason explicitly states that Risk approval is still required;
- fixed 1:2 CR-012 remains the unchanged benchmark;
- no Forward, Strategy Tester Runtime, Shadow Execution, or broker behavior is
  changed by Stage A.

## Focused validation

`tests/TestHybridRuleTradePlan.mq5` checks:

- valid BUY and SELL structural plans;
- preservation of an adaptive RR above fixed 1:2;
- rejection of missing POI confirmation;
- rejection of invalid Stop/Target geometry;
- rejection of open-bar input;
- rejection of a nearest target below minimum RR;
- explicit preservation of the final Risk boundary.

## Synchronization and compile tools

- `tools/sync_hybrid_rule_trade_plan_research_to_mt5.ps1`
- `tools/compile_hybrid_rule_trade_plan_research.ps1`

Dataset export and all downstream gates are complete. These tools may run after
MT5/MetaEditor have been closed normally.

## Known limitations

- Stage A consumes explicit confluence flags; it does not yet calculate M15/M5/
  M1 indicators or detect POI/trigger structures.
- Stage A validates one nearest structural target; partial exits and trailing
  logic are outside scope.
- Stage A does not size volume or approve Risk.
- Stage A is not connected to Runtime or Shadow Execution.
- MetaEditor compilation and focused EA output are pending.

## Workspace validation

- focused include closure: 6 files;
- missing local includes: 0;
- broker-capable files or mutation tokens in focused closure: 0;
- one-class-per-MQH check: 5/5;
- PowerShell tool parse: 2/2;
- canonical Shadow closure: 108 files, 0 broker-capable files, 0 mutation
  tokens;
- complete Python script regression: 33/33 passed;
- MetaEditor compile: passed on 2026-07-18 after SHA-256 verified MT5
  synchronization; the focused target compiled with `0 errors / 0 warnings`.
- Focused MT5 contract validation passed on XAUUSD M15 at
  `2026.07.18 22:43:02.349`: BUY/SELL structural plans, adaptive RR above 2R,
  missing-POI rejection, invalid-geometry rejection, open-bar rejection,
  insufficient nearest-target rejection, and the final Risk boundary all
  reported `true`.

## Next controlled stage

After the corrected Dataset gates and CR-012 benchmark are complete, define and
test an objective past-only multi-timeframe adapter that supplies this contract.
Runtime integration remains a separate evidence gate.
