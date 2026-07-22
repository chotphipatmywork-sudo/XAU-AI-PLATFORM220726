# XAU-AI-PLATFORM Architecture

Version: 1.0.0

Status: Architecture Alignment Draft

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the Single Source of Truth architecture for the XAU-AI-PLATFORM system.

The purpose is to establish one canonical runtime flow, module responsibility boundaries, and dependency direction before Architecture Freeze.

All source code, documentation, and future development decisions must align with this architecture.

---

## 1. Canonical Runtime Path

The XAU-AI-PLATFORM system has one production runtime path.

The canonical flow is:

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

Any alternative application entry flow is considered non-canonical and must not be used as a production execution path.

---

## 2. Application Entry Ownership

The production entry point is:

```text
XAU-AI-PLATFORM.mq5
```

Responsibilities:

* Initialize system lifecycle
* Start Kernel
* Start Runtime
* Register required modules
* Control application startup and shutdown

The entry point must not contain trading intelligence or module business logic.

---

## 3. Kernel Responsibility

Kernel is the system foundation layer.

Responsibilities:

* Application lifecycle control
* Module registration
* Dependency initialization
* Runtime preparation

Kernel does not perform:

* Market analysis
* Trading decisions
* Risk calculation
* Order execution

---

## 4. Runtime Responsibility

Runtime is responsible for system operation.

Responsibilities:

* Event processing
* Tick handling
* Scheduling
* Module execution coordination

Runtime connects infrastructure with business modules.

---

## 5. Core Module Flow

The business execution flow is:

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

Each layer has a defined responsibility.

---

## 6. Module Responsibility Boundary

### 6.1 Market Module

Input:

* Price data
* Indicators
* Market information

Output:

* Market Context

Market does not make trading decisions.

---

### 6.2 Brain Module

Input:

* Market Context

Output:

* Signal analysis
* Market interpretation
* Decision proposal

Brain is responsible for understanding market conditions.

Brain does not:

* Approve risk
* Manage money
* Execute orders

---

### 6.3 AI Runtime

Input:

* Brain output
* Features
* Context

Output:

* AI scoring
* Confidence calculation
* Decision support

AI Runtime improves decision quality.

---

### 6.4 Decision Module

Input:

* AI Runtime result

Output:

* Trading decision

Examples:

* BUY
* SELL
* HOLD

Decision represents intention only.

---

### 6.5 Risk Module

Input:

* Trading decision

Output:

* Risk approval
* Position sizing
* Risk constraints

Risk is the final safety gate before execution.

---

### 6.6 Execution Module

Input:

* Approved trading decision

Output:

* Real order operation

Execution owns:

* Trade request creation
* Order validation
* Order submission
* Execution result

Execution must connect to Trade Executor.

---

### 6.7 Trade Lifecycle Module

Responsible for:

* Position state tracking
* Trade state transition
* Exit management
* Trade monitoring

---

### 6.8 Portfolio Module

Responsible for:

* Account-level management
* Exposure monitoring
* Portfolio state

---

### 6.9 Learning Module

Responsible for:

* Performance analysis
* Model improvement
* Adaptive learning

---

## 7. Dependency Direction Rule

All dependencies must follow:

```text
Upper Layer

      ↓

Lower Layer
```

Allowed:

```text
Brain

↓

Decision

↓

Risk

↓

Execution
```

Not allowed:

```text
Brain

↓

Engine

↓

Brain
```

or:

```text
Execution

↓

Trade

↓

Execution
```

Circular dependency is prohibited.

---

## 8. Architecture Rules

### Rule 1 — Single Runtime Path

Only one production runtime path is allowed.

---

### Rule 2 — Layer Ownership

Each module owns only its defined responsibility.

---

### Rule 3 — No Upward Dependency

Lower layers must not depend on higher layers.

---

### Rule 4 — No Hidden Execution Path

Every trading action must follow:

```text
Decision

↓

Risk

↓

Execution

↓

Trade Lifecycle
```

---

## 9. Architecture Freeze Condition

Architecture Freeze will happen only after:

* Canonical Runtime Path validated
* Dependency Direction validated
* Execution ownership validated
* Documentation aligned
* Codex audit confirms no architectural contradiction

Until then:

```text
Architecture Freeze: BLOCKED
```

---

## 10. Next Architecture Decisions

The following ADR documents must be created:

* ADR-001 Canonical Runtime Path
* ADR-002 Module Dependency Direction
* ADR-003 Risk Boundary
* ADR-004 Execution Ownership

These decisions become permanent architecture references after approval.
