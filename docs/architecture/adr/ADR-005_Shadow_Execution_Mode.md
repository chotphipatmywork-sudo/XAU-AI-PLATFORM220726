# ADR-005 Shadow Execution Mode

Version: 1.0.0

Date: 2026-07-16

Status: Approved

Architecture Baseline: ABR-1.0

## Context

Phase 7 closed with model deployment denied. The platform still needs
end-to-end operational evidence for Runtime, Risk, Execution, lifecycle,
logging, and monitoring. Invoking the existing broker-capable executor would
create unacceptable risk.

## Decision

Execution supports explicit modes:

- `EXECUTION_MODE_SHADOW`: simulate and audit only;
- `EXECUTION_MODE_LIVE_LOCKED`: reject execution;
- a future live-enabled mode may be introduced only by another approved ADR.

The canonical Shadow path is:

`Decision -> Risk approval -> Shadow Execution -> Paper Trade Lifecycle`

Execution accepts a concrete Risk result. A Boolean check performed elsewhere
is insufficient evidence at the Execution boundary.

## Ownership

- Decision owns trading intent.
- Risk owns permission, sizing constraints, and emergency stop.
- Execution selects the approved adapter.
- Shadow Execution owns simulated fills only.
- Paper Trade Lifecycle owns simulated position state and exits.
- Telemetry owns observation and reporting.

## Consequences

- The complete pipeline can run without broker mutation.
- Risk approval becomes auditable at the execution boundary.
- Existing broker execution remains present but unreachable from Shadow mode.
- Public Runtime and Execution interfaces require a controlled migration under
  CR-008.

## Validation

- focused tests prove rejected Risk cannot create a paper trade;
- focused tests prove approved BUY/SELL creates only a synthetic ticket;
- broker position and order counts remain unchanged;
- duplicate signals cannot create a second paper position;
- emergency stop blocks new entries;
- MetaEditor reports zero errors and zero warnings.
