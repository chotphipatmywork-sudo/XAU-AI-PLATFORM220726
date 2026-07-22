# ADR-001 Canonical Runtime Path

Version: 1.0.0

Status: Approved Draft

Architecture Baseline: ABR-1.0

---

## Context

The XAU-AI-PLATFORM system currently contains multiple application entry flows identified during the Core Audit.

The audit found:

```text
XAU-AI-PLATFORM.mq5
        ↓
CCore
        ↓
CRuntimeManager
```

Alternative flow:

```text
CCoreEngine
        ↓
CAIApplication
        ↓
CSystemManager
```

Kernel flow:

```text
CKernel
        ↓
CApplication
        ↓
CModuleRegistry
```

Multiple runtime paths create architectural ambiguity.

Before Architecture Freeze, the system must define one canonical production runtime path.

---

## Decision

The XAU-AI-PLATFORM system will use one canonical production runtime path.

The official runtime path is:

```text
XAU-AI-PLATFORM.mq5

        ↓

Kernel

        ↓

Runtime

        ↓

Market

        ↓

Brain

        ↓

AI Runtime

        ↓

Decision

        ↓

Risk

        ↓

Execution

        ↓

Trade Lifecycle

        ↓

Portfolio

        ↓

Learning
```

This path is the only approved production execution flow.

---

## Runtime Ownership

### Application Entry

`XAU-AI-PLATFORM.mq5`

Responsibilities:

* Start application lifecycle
* Initialize Kernel
* Start Runtime
* Trigger module initialization

The application entry point must not contain business logic.

---

### Kernel

Responsibilities:

* System initialization
* Module registration
* Dependency preparation
* Lifecycle control

Kernel does not perform:

* Market analysis
* Trading decisions
* Risk management
* Order execution

---

### Runtime

Responsibilities:

* Event processing
* Tick dispatching
* Scheduler operation
* Module coordination

Runtime provides execution infrastructure for the business pipeline.

---

## Rejected Runtime Paths

The following flows are not production paths:

```text
CCoreEngine
        ↓
CAIApplication
        ↓
CSystemManager
```

and:

```text
CKernel
        ↓
CApplication
        ↓
CModuleRegistry
```

These components may remain as implementation candidates only if they comply with the canonical architecture.

They must not create independent application execution flows.

---

## Consequences

### Positive Consequences

* Single system startup model
* Clear lifecycle ownership
* Easier debugging
* Easier testing
* Reduced architectural ambiguity
* Better dependency control

---

### Negative Consequences

* Existing alternative startup paths may require refactoring
* Some legacy components may become obsolete

---

## Validation Criteria

The architecture is considered compliant when:

* Only one production entry path exists
* Runtime initialization follows the canonical flow
* No alternative application startup bypasses Kernel or Runtime
* Module execution follows the defined pipeline
* Codex Architecture Audit confirms no runtime conflict

---

## Related Decisions

Related ADRs:

* ADR-002 Module Dependency Direction
* ADR-003 Risk Boundary
* ADR-004 Execution Ownership

---

## Decision Status

```text
Canonical Runtime Path: APPROVED

Architecture Freeze Impact:
Required Before Freeze
```
