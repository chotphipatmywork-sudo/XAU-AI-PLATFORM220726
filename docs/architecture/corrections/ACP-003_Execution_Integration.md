# ACP-003 Execution Integration

Version: 1.0.0

Status: Draft

Architecture Baseline: ABR-1.0

---

## Purpose

This Architecture Correction Plan defines the implementation changes required to complete the production execution chain.

The objective is to ensure that every Risk-approved trading request reaches the Trade Executor and that the resulting broker response is handed over to the Trade Lifecycle module.

---

## Related Findings

### Codex Architecture Compliance Audit Round 2

| Finding   | Severity | Description                                        |
| --------- | -------- | -------------------------------------------------- |
| Finding 5 | A        | Execution pipeline stops before Trade Executor     |
| Finding 6 | B        | Execution does not receive a Risk-approved request |
| Finding 7 | B        | Duplicate Trade Lifecycle ownership                |

---

## Related Architecture Decisions

* ADR-003 Risk Boundary
* ADR-004 Execution Ownership

---

## Objective

Establish the approved production execution chain.

Approved execution flow:

```text
Decision

↓

Risk

↓

Execution Pipeline

↓

Trade Manager

↓

Trade Executor

↓

Trade Lifecycle

↓

Portfolio
```

Execution shall never terminate at an intermediate result object.

---

## Current State

The current implementation builds an `ExecutionResult` but does not invoke the production trade execution path.

Observed issues include:

* Execution ends before broker communication.
* Trade Executor is disconnected from the active execution pipeline.
* Execution generates default position size values.
* Trade Lifecycle ownership is duplicated.

These issues prevent the production execution chain from completing.

---

## Target State

Execution shall become the single owner of trade execution.

Execution responsibilities include:

* Validate Risk-approved request
* Build broker request
* Invoke Trade Manager
* Invoke Trade Executor
* Receive broker response
* Publish execution event

Trade Lifecycle shall become the only consumer of successful execution events.

---

## Root Cause Analysis

Earlier development focused on pipeline validation before broker integration.

As implementation expanded, broker execution components were added independently, leaving the production pipeline incomplete.

This resulted in:

* Disconnected execution stages
* Duplicate lifecycle ownership
* Incomplete execution flow

---

## Files Expected To Be Modified

Potential implementation targets include:

```text
core/execution/

core/trade/

core/runtime/
```

Specific implementation files shall be confirmed before modification.

---

## Refactoring Strategy

### Step 1

Require Execution to accept only a Risk-approved request.

---

### Step 2

Connect Execution Pipeline to Trade Manager.

---

### Step 3

Connect Trade Manager to Trade Executor.

---

### Step 4

Return the broker execution result to the Execution module.

---

### Step 5

Emit a single execution event.

---

### Step 6

Transfer execution ownership to Trade Lifecycle.

TradeLifecycle shall be instantiated only once in the production runtime.

---

## Risks

Potential implementation risks include:

* Broker interface changes
* Request model updates
* Event propagation changes
* Runtime ownership adjustments

Each implementation step shall be verified independently.

---

## Validation Criteria

This correction is complete when:

* Execution reaches Trade Manager.
* Trade Manager reaches Trade Executor.
* Trade Executor communicates with the broker.
* Broker response returns to Execution.
* Trade Lifecycle receives one execution event.
* Execution no longer creates default position sizes.
* Codex reports no Finding 5.
* Codex reports no Finding 6.
* Codex reports no Finding 7.

---

## Completion Checklist

| Item                              | Status |
| --------------------------------- | ------ |
| Risk-approved request implemented | ☐      |
| Trade Manager integrated          | ☐      |
| Trade Executor connected          | ☐      |
| Broker response returned          | ☐      |
| Single Trade Lifecycle owner      | ☐      |
| Codex verification passed         | ☐      |
| ACP approved                      | ☐      |

---

## Exit Criteria

ACP-003 may be closed only after the production execution chain is complete and all related findings have been resolved in accordance with ADR-003 and ADR-004.
