# IMP-059 Shadow Trading Safety Foundation

Status: Implemented and compiled; focused runtime execution pending

Related: CR-008, ADR-003, ADR-004, ADR-005

## Purpose

Build the non-broker foundation for Phase 8A before canonical Runtime wiring.

## Initial components

- explicit execution-mode model;
- immutable execution authorization assembled from Decision and Risk;
- paper trade state and synthetic ticket sequence;
- one-position Shadow execution engine;
- append-only CSV audit logger;
- focused test EA that records broker order/position counts before and after.

## Initial acceptance criteria

- no Shadow source includes the MQL5 Trade library;
- invalid or rejected Risk results are refused;
- HOLD/WAIT is refused as an entry;
- approved BUY/SELL produces a synthetic result;
- a second entry is refused while the paper position is active;
- emergency stop refuses an entry;
- audit CSV records every outcome;
- no live order or position count changes during the focused test.

## Implemented boundary

- Runtime processes one closed M15 bar at a time using Brain shift `1`.
- AI output is converted by the Decision layer into explicit intent.
- Risk consumes the intent plus Shadow exposure, paper loss, drawdown, and
  stale-market context.
- Shadow Execution consumes both Decision and Risk result.
- Paper entries include spread and simulated slippage.
- Paper lifecycle closes on SL, TP, or maximum holding time.
- Telemetry writes a 60-second heartbeat with both deployment authorization
  flags permanently false.
- Emergency stop is available as an EA input and is applied to Risk and Shadow
  Execution together.
- Paper volume, SL/TP points, simulated slippage, maximum holding bars, paper
  daily loss, paper drawdown, and maximum tick age are explicit EA Inputs
  carried through one validated Runtime configuration.
- A terminal Global Variable checkpoints the last processed closed bar per
  account, symbol, and timeframe so restarting the EA does not duplicate a
  decision record.
- The checkpoint uses an atomic terminal-global compare-and-set so two charts
  cannot claim the same account/symbol/timeframe bar concurrently.
- Emergency stop and normal EA shutdown close any active paper state with an
  auditable reason; neither action contacts the broker.
- Paper state is persisted separately and can be recovered after an abnormal
  terminal restart. A recovered synthetic ticket remains isolated from broker
  positions.

## Focused tests

- `tests/TestClosedBarBrainContext.mq5`
- `tests/TestShadowRiskGate.mq5`
- `tests/TestShadowExecutionSafety.mq5`

## Compile validation

MetaEditor compiled the synchronized MT5 project copy on 2026-07-16:

- `tests/TestClosedBarBrainContext.mq5`: 0 errors, 0 warnings
- `tests/TestShadowRiskGate.mq5`: 0 errors, 0 warnings
- `tests/TestShadowExecutionSafety.mq5`: 0 errors, 0 warnings
- `XAU-AI-PLATFORM.mq5`: 0 errors, 0 warnings

Compile logs:

- `outputs/compile/shadow/TestClosedBarBrainContext.log`
- `outputs/compile/shadow/TestShadowRiskGate.log`
- `outputs/compile/shadow/TestShadowExecutionSafety.log`
- `outputs/compile/shadow/XAU-AI-PLATFORM.log`

The generated `.ex5` files were verified present in the MT5 project copy. The
canonical no-broker closure audit covered 96 files and found zero
broker-capable files and zero broker-mutation tokens.

## Focused runtime evidence

On XAUUSD M15 at 2026-07-16 22:01:25:

- closed-bar Trend context: true
- closed-bar Liquidity context: true
- closed-bar Session timing: true
- complete closed-bar Brain context: true
- focused EA removed itself normally

On XAUUSD M15 at 2026-07-16 22:02:38:

- safe-default Shadow execution mode and live lock: true
- clear-context explicit Risk approval: true
- active paper exposure blocked: true
- stale market blocked: true
- paper daily-loss limit blocked: true
- paper drawdown limit blocked: true
- emergency stop blocked: true
- complete Shadow Risk gate: true
- focused EA removed itself normally

On XAUUSD M15 at 2026-07-16 22:04:50:

- rejected Risk could not open paper state: true
- approved Risk opened a synthetic paper entry: true
- duplicate entry protection: true
- active paper-state recovery after reinitialization: true
- paper take-profit lifecycle: true
- emergency stop: true
- broker order and position counts unchanged: true
- complete Shadow execution safety: true
- focused EA removed itself normally

## Canonical Shadow Runtime evidence

The canonical `XAU-AI-PLATFORM` EA was attached to XAUUSD M15 on the Demo
terminal at 2026-07-16 22:09:31 with Algo Trading disabled and
`ShadowEmergencyStop=false`.

- Shadow Runtime startup completed.
- model deployment authorization remained false.
- live execution authorization remained false.
- the first closed-bar pipeline evaluation used the 2026-07-16 17:45 bar.
- AI produced a SELL decision with confidence 36.91562042268257.
- Risk explicitly approved the decision with risk score 100.
- Shadow Execution opened synthetic ticket 900000001.
- the audit message explicitly recorded that no broker order was sent.
- the first heartbeat reported one decision, zero Risk rejections, one
  synthetic execution, and one active paper position.
- the 60-second follow-up telemetry row retained
  `live_execution_authorized=false`.

The generated Decision, Audit, Telemetry, and State records agreed on the
closed bar, synthetic ticket, active paper state, and non-live authorization.
The recorded model status remained `DEVELOPMENT_HEURISTIC_MODEL_NO_GO`; this
runtime evidence validates the Shadow pipeline and does not authorize model or
live deployment.

## Operational files

- `MQL5/Files/XAU_AI_SHADOW_AUDIT.csv`
- `MQL5/Files/XAU_AI_SHADOW_DECISIONS.csv`
- `MQL5/Files/XAU_AI_SHADOW_TELEMETRY.csv`
- `MQL5/Files/XAU_AI_SHADOW_STATE.csv`

Decision evidence includes closed-bar OHLC and ATR so the offline evaluator can
wait for 16 later observations and reproduce Label Schema 1.1 without reading
forming bars or the historical Validation/Test partitions.
