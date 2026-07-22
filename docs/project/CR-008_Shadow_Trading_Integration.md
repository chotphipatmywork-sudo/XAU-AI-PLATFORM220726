# CR-008 Shadow Trading Integration

Version: 1.0.0

Date: 2026-07-16

Status: Approved for phased implementation

Architecture Baseline: ABR-1.0

Related Phase: Phase 8A — Shadow Trading Integration

## Approval

The project owner approved implementation of the complete Shadow workflow,
including pipeline integration, paper execution, safety controls, monitoring,
forward testing, accuracy improvement, and a later gated deployment path.

This approval does not authorize live orders or reuse of inspected Validation
or Test evidence.

## Problem

The canonical Runtime reaches the broker-capable Execution layer, but it does
not yet provide an explicit execution-mode lock or carry a concrete Risk
approval object into Execution. The current model evidence remains a Phase 7
NO-GO with zero complete passing folds.

The platform needs to exercise the complete business flow without exposing the
account to broker orders:

`Market -> Brain -> AI Runtime -> Decision -> Risk -> Shadow Execution -> Paper Trade Lifecycle`

## Approved change

1. Add an explicit execution mode with `SHADOW` as the safe default.
2. Require a valid, approved Risk result at the Execution boundary.
3. Add a paper position lifecycle that never calls `CTrade`.
4. Write an append-only audit record for every intent, rejection, simulated
   open, update, and close.
5. Add one-position, daily-loss, drawdown, emergency-stop, stale-market, and
   duplicate-bar protections.
6. Expose health and performance snapshots for Strategy Tester and forward
   observation.
7. Keep live execution locked until a separate deployment approval.

## Safety invariants

- Shadow code must not include `<Trade/Trade.mqh>`.
- Shadow mode must never call `CTrade`, `OrderSend`, `PositionClose`, or any
  broker mutation API.
- Execution must reject missing, invalid, blocked, or emergency Risk results.
- The model-quality NO-GO must be visible in Runtime configuration and logs.
- Shadow and live positions must not share state.
- One decision may be processed at most once per closed observation bar.
- A closed bar older than the configured decision-lag limit must be
  checkpointed and skipped after startup or restart.
- HOLD/WAIT is auditable but cannot open a paper position.
- Live mode requires a separate compile-time and runtime authorization that is
  outside CR-008.

## Delivery stages

### 8A.1 Safety foundation

Execution mode, explicit Risk approval contract, paper position state, audit
log, and focused synthetic tests.

### 8A.2 Canonical Runtime integration

Insert the Decision layer explicitly, pass the Decision to Risk, and pass both
Decision and Risk approval to Shadow Execution.

### 8A.3 Paper lifecycle

Simulated entry, mark-to-market, SL/TP exit, maximum holding time, spread and
slippage accounting, and one-position enforcement.

### 8A.4 Monitoring and protection

Heartbeat, last processed bar, rejection reasons, daily paper P/L, drawdown,
emergency stop, stale data detection, and CSV health snapshots.

### 8A.5 Test operations

Strategy Tester validation followed by forward Shadow observation on Demo.
No broker order is allowed.

### 8A.6 Model improvement and deployment gate

Use only new Shadow observations and separately approved public market
context. Retraining remains offline. Shadow or live deployment requires fresh
untouched evaluation and explicit approval.

## Compatibility

Feature Schema 4.0 and Label Schema 1.1 remain unchanged. Brain, AI training,
Risk ownership, and live broker ownership remain separate.

## Rollback

Remove the Shadow adapter, configuration, tests, and Runtime wiring; restore
the prior Runtime interfaces. No broker position needs rollback because CR-008
does not authorize live execution.
