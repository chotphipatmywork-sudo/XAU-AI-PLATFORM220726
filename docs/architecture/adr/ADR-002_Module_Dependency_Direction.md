# ADR-002 Module Dependency Direction

Version: 1.0.0

Status: Approved Draft

Architecture Baseline: ABR-1.0

---

## Context

The XAU-AI-PLATFORM Core Audit identified dependency conflicts inside the current implementation.

Observed issues include:

```text
Brain

↓

Engine

↓

Brain
```

and:

```text
Execution

↓

Trade

↓

Execution
```

These patterns create circular dependency risks.

Circular dependencies reduce:

* Module independence
* Testability
* Maintainability
* Architecture stability

Before Architecture Freeze, the system must define a permanent dependency direction rule.

---

## Decision

The XAU-AI-PLATFORM architecture follows a one-direction dependency model.

The official rule is:

```text
Upper Layer

        ↓

Lower Layer
```

Higher-level modules may depend on lower-level modules.

Lower-level modules must not depend on higher-level modules.

---

## Approved Module Dependency Flow

The approved business dependency direction is:

```text
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

Dependencies must follow this direction only.

---

## Layer Dependency Rules

## Market Layer

Market provides:

* Price data
* Market information
* Indicators
* Context data

Market must not depend on:

* Brain
* Decision
* Risk
* Execution

---

## Brain Layer

Brain consumes:

* Market Context

Brain provides:

* Market interpretation
* Signal analysis
* Decision proposal

Brain must not depend on:

* Risk
* Execution
* Trade Lifecycle

---

## AI Runtime Layer

AI Runtime consumes:

* Brain output
* Features
* Context

AI Runtime provides:

* Scoring
* Confidence
* Decision support

AI Runtime must not control:

* Risk approval
* Order execution

---

## Decision Layer

Decision consumes:

* AI Runtime result

Decision provides:

* BUY
* SELL
* HOLD
* Trading intent

Decision must not:

* Execute orders
* Manage positions
* Override risk

---

## Risk Layer

Risk consumes:

* Trading decision

Risk provides:

* Risk approval
* Position sizing
* Risk constraints

Risk must not depend on:

* Execution internals
* Trade implementation details

---

## Execution Layer

Execution consumes:

* Approved decisions
* Risk approval

Execution provides:

* Order operation
* Execution result

Execution must not create dependency back to:

* Decision
* Brain
* Market

---

## Trade Lifecycle Layer

Trade Lifecycle consumes:

* Execution results

Trade Lifecycle provides:

* Position state
* Trade state transitions
* Exit management

Trade Lifecycle must not control:

* Order creation logic

---

## Circular Dependency Rule

The following dependency patterns are prohibited:

```text
A

↓

B

↓

A
```

or:

```text
Module X

↓

Module Y

↓

Module X
```

All circular dependencies must be removed before Architecture Freeze.

---

## Dependency Ownership Rule

Each module owns its own responsibility.

Example:

Correct:

```text
Brain

↓

Decision

↓

Risk

↓

Execution
```

Incorrect:

```text
Brain

↓

Risk Approval
```

Incorrect:

```text
Execution

↓

Brain Analysis
```

---

## Consequences

### Positive Consequences

* Clear module boundaries
* Reduced coupling
* Easier unit testing
* Better maintainability
* Safer future expansion

---

### Negative Consequences

* Some existing dependencies may require refactoring
* Legacy modules may need restructuring

---

## Validation Criteria

The architecture is compliant when:

* No circular dependencies exist
* Dependency direction follows the approved flow
* Modules only access allowed lower layers
* Interfaces are used between independent layers
* Codex dependency audit confirms compliance

---

## Related Decisions

Related ADRs:

* ADR-001 Canonical Runtime Path
* ADR-003 Risk Boundary
* ADR-004 Execution Ownership

---

## Decision Status

```text
Module Dependency Direction: APPROVED

Architecture Freeze Impact:
Required Before Freeze
```
