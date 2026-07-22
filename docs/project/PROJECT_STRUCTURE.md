# XAU AI PLATFORM — PROJECT STRUCTURE

Version: 1.0.0

Status: Frozen

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the official directory structure
of the XAU AI PLATFORM.

Every source file must be placed in its designated location.

The objective is to maintain:

* Clear ownership.
* Controlled module boundaries.
* Predictable project organization.
* Architecture consistency.

---

## Official Root Structure

```text
XAU-AI-PLATFORM/

├── .vscode/
├── assets/
├── core/
├── docs/
├── releases/
├── research/
├── scripts/
├── tests/
├── tools/

├── README.md
├── ROADMAP.md
├── CHANGELOG.md
└── LICENSE.md
```

---

## Core Module Structure

```text
core/

├── ai/
├── application/
├── backtest/
├── brain/
├── common/
├── config/
├── dashboard/
├── data/
├── decision/
├── engine/
├── execution/
├── indicators/
├── infrastructure/
├── interfaces/
├── kernel/
├── logging/
├── market/
├── money/
├── optimizer/
├── portfolio/
├── position/
├── risk/
├── runtime/
├── scheduler/
├── system/
├── telemetry/
└── trade/
```

---

## Foundation Modules

The following modules form the core trading pipeline.

---

## Runtime Module

Directory:

```text
core/runtime/
```

Responsibility:

* Application lifecycle.
* Initialization.
* Tick processing.
* Timer handling.
* Shutdown management.

---

## Market Module

Directory:

```text
core/market/
```

Responsibility:

* Market data.
* Market analysis.
* Market context.
* Market detectors.

---

## AI Module

Directory:

```text
core/ai/
```

Responsibility:

* Artificial Intelligence processing.
* Signal generation.
* Confidence calculation.
* Model integration.

---

## Decision Module

Directory:

```text
core/decision/
```

Responsibility:

* Trading decision processing.
* Signal validation.
* Decision building.

---

## Risk Module

Directory:

```text
core/risk/
```

Responsibility:

* Risk management.
* Exposure control.
* Position sizing.
* Risk validation.

---

## Execution Module

Directory:

```text
core/execution/
```

Responsibility:

* Trade execution.
* Order management.
* Execution processing.

---

## Common Module

Directory:

```text
core/common/
```

Responsibility:

* Shared utilities.
* Reusable helpers.
* Common models.

---

## Configuration Module

Directory:

```text
core/config/
```

Responsibility:

* Configuration management.
* System settings.
* Environment settings.

---

## Logging Module

Directory:

```text
core/logging/
```

Responsibility:

* Logging.
* Debug information.
* Performance monitoring.

---

## Supporting Modules

| Module         | Responsibility                           |
| -------------- | ---------------------------------------- |
| application    | Application orchestration                |
| brain          | Market intelligence and feature analysis |
| engine         | Pipeline orchestration                   |
| data           | Data providers                           |
| indicators     | Indicator providers and cache            |
| portfolio      | Portfolio management                     |
| position       | Position lifecycle                       |
| money          | Money management                         |
| optimizer      | Optimization engine and testing          |
| backtest       | Historical simulation                    |
| scheduler      | Event scheduling                         |
| system         | System state management                  |
| telemetry      | Metrics and monitoring                   |
| trade          | Trade lifecycle                          |
| dashboard      | User interface and visualization         |
| interfaces     | Public interfaces                        |
| infrastructure | Infrastructure services                  |

---

## Documentation Structure

```text
docs/

├── architecture/
├── baseline/
├── codex/
├── development/
├── project/
├── standards/
└── templates/
```

Responsibilities:

| Directory    | Purpose                 |
| ------------ | ----------------------- |
| architecture | Architecture references |
| baseline     | Baseline documentation  |
| codex        | Codex workflow          |
| development  | Development guides      |
| project      | Project governance      |
| standards    | Coding standards        |
| templates    | Project templates       |

---

## Test Structure

Directory:

```text
tests/
```

Contains:

* Unit tests.
* Integration tests.
* Performance tests.

---

## Script Structure

Directory:

```text
scripts/
```

Contains:

* Automation.
* Build scripts.
* Validation tools.

---

## Directory Rules

The following rules are mandatory:

* One responsibility per directory.
* One owner per module.
* No duplicate modules.
* No cross-layer business logic.
* No business logic inside documentation.
* New top-level directories require Architecture Review.
* New modules require approved Change Request.

---

## Architecture Freeze

This directory structure is frozen.

Any structural changes require:

* Approved Change Request.
* Architecture Review.
* Implementation approval.

---

## Related Documents

* ARCHITECTURE_PRINCIPLES.md
* ARCHITECTURE_DECISIONS.md
* ARCHITECTURE_FREEZE.md
* MODULE_DEPENDENCY_RULES.md
* MODULE_INTERFACE_CATALOG.md
* DOCUMENTATION_GOVERNANCE.md

---

## Document Status

Document:

`PROJECT_STRUCTURE.md`

Review Phase:

Phase 0.3 — Foundation Architecture Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

---

End of PROJECT_STRUCTURE.md
