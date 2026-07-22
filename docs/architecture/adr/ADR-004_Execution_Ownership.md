# ADR-004 Execution Ownership

Version: 1.0.0

Status: Approved Draft

Architecture Baseline: ABR-1.0

---

## Context

The XAU-AI-PLATFORM Core Audit identified a critical execution boundary issue.

The observed flow:

```text id="4h6k2z"
ExecutionPipeline

↓

ExecutionResult

↓

X

↓

TradeExecutor
```

The system was able to produce execution analysis results, but the ownership of actual order execution was unclear.

A production trading system requires a complete execution chain from approved decision to real trade operation.

Before Architecture Freeze, Execution ownership must be explicitly defined.

---

## Decision

The XAU-AI-PLATFORM architecture defines the Execution Module as the owner of trade operation.

The approved trading execution flow is:

```text id="f9s2jw"
Decision

↓

Risk Approval

↓

Execution Pipeline

↓

Trade Executor

↓

Trade Lifecycle

↓

Portfolio
```

Execution is responsible for converting approved trading intent into actual broker operations.

---

## Execution Responsibility

The Execution Module owns:

* Trade request creation
* Order validation
* Broker communication
* Order submission
* Execution result handling
* Execution error handling

Execution receives:

```text id="3k8n5v"
Risk Approved Decision
```

Execution produces:

```text id="m1q7wx"
Execution Result

+

Trade Lifecycle Event
```

---

## Execution Pipeline Ownership

The Execution Pipeline controls the execution sequence:

```text id="j5x9pk"
Analyze

↓

Validate

↓

Position Check

↓

Build Trade Request

↓

Assembler

↓

Trade Executor

↓

Return Execution Result
```

The pipeline must guarantee that every approved trade request reaches the Trade Executor.

---

## Trade Executor Responsibility

Trade Executor owns:

* Sending orders to broker
* Receiving broker responses
* Reporting execution status

Trade Executor does not own:

* Market analysis
* Decision generation
* Risk calculation

---

## Risk Enforcement Rule

Execution must not bypass Risk.

Allowed:

```text id="2v8f6y"
Decision

↓

Risk

↓

Execution

↓

Trade Executor
```

Not allowed:

```text id="6r3n9w"
Decision

↓

Execution

↓

Trade Executor
```

---

## Trade Lifecycle Boundary

After successful execution:

```text id="w4m8cz"
Trade Executor

↓

Trade Lifecycle

↓

Portfolio
```

Trade Lifecycle owns:

* Position state
* Trade state transitions
* Exit management
* Trade monitoring

Execution does not manage the complete trade lifecycle.

---

## Error Ownership

Execution owns execution-related errors:

Examples:

* Order rejection
* Invalid request
* Broker failure
* Execution timeout

Risk owns risk-related rejection:

Examples:

* Risk limit exceeded
* Position size violation
* Exposure violation

---

## Prohibited Responsibilities

### Execution Performing Decision Logic

```text id="k5m1qz"
Execution

↓

Market Decision
```

Not allowed.

---

### Trade Lifecycle Creating Orders

```text id="r7p3vx"
Trade Lifecycle

↓

Order Creation
```

Not allowed.

---

### Risk Sending Orders

```text id="n2v6hs"
Risk

↓

Broker Order
```

Not allowed.

---

## Consequences

### Positive Consequences

* Clear order ownership
* Complete execution chain
* Easier debugging
* Better failure handling
* Production-ready trading flow

---

### Negative Consequences

* Existing execution components may require integration changes
* Trade Executor interface may require validation

---

## Validation Criteria

The architecture is compliant when:

* ExecutionPipeline reaches TradeExecutor
* Risk approval is mandatory before execution
* Trade execution ownership is clearly defined
* Execution errors are handled inside Execution Layer
* Trade Lifecycle receives execution events
* Codex audit confirms execution completeness

---

## Related Decisions

Related ADRs:

* ADR-001 Canonical Runtime Path
* ADR-002 Module Dependency Direction
* ADR-003 Risk Boundary

---

## Decision Status

```text id="a6k9qp"
Execution Ownership: APPROVED

Architecture Freeze Impact:
Required Before Freeze
```
