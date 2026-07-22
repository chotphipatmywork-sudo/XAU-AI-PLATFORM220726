# XAU AI PLATFORM — ARCHITECTURE FREEZE

Version : 1.0.0

Status : FROZEN

Architecture Baseline : ABR-1.0

---

## Purpose

This document defines the frozen architecture baseline
of the XAU AI PLATFORM.

All future development must follow this architecture
unless an approved Change Request exists.

This document establishes:

- Architecture boundaries.
- Ownership rules.
- Migration requirements.
- Change control requirements.

---

## Scope

This document defines:

- Frozen architecture boundaries.
- Approved architecture decisions.
- Migration rules.
- Architecture ownership rules.
- Architecture change control requirements.

This document applies to all future development
activities of the XAU AI PLATFORM.

---

## Current Implementation

This section describes the current implementation
of the project.

The implementation may differ from the frozen architecture
during the transition period.

---

## Market Module

### Current Structure

```text
MarketManager
    └── MarketProvider
            └── MarketEngine
Status

Legacy Implementation

Notes
Current implementation is accepted temporarily.
Compile compatibility must be preserved.
Refactoring will be performed during migration.
New development must follow the Target Architecture.
Target Architecture

This section defines the frozen architecture
that must be used for future development.

Market Module Target Architecture
Target Structure
MarketManager
├── MarketProvider
└── MarketEngine
Responsibilities
MarketProvider

Responsibilities:

Provide market data only.
No market analysis.
No detector ownership.
No engine ownership.
MarketEngine

Responsibilities:

Coordinate market analysis.
Execute detectors.
Build MarketContext.
MarketManager

Responsibilities:

Provide the public API of the Market Module.
Coordinate MarketProvider and MarketEngine.
Maintain module boundary integrity.
Architecture Decision
Decision ID

MARKET-001

Decision

MarketProvider and MarketEngine are sibling components
coordinated by MarketManager.

Rationale
Clear separation of responsibilities.
Single Responsibility Principle.
Easier testing and maintenance.
Prevent hidden ownership between modules.
Support future module expansion.
Status

ACCEPTED

Non-Negotiable Architecture Rules

The following rules are mandatory:

Frozen architecture shall not be bypassed.
New modules shall follow approved ownership boundaries.
Interfaces shall not be changed without review.
Dependencies shall follow dependency rules.
Legacy structures shall not be extended.
Each responsibility shall have a single owner.
Circular dependencies are prohibited.
Hidden ownership is prohibited.
Migration Rules

During the migration period:

Existing implementation may remain for compatibility.
New code must follow the Target Architecture.
No new dependencies may use the legacy ownership model.
Public APIs must remain backward compatible.
Legacy ownership shall be removed after migration is complete.
Migration Roadmap
Phase 1

Current:

MarketManager
    └── MarketProvider
            └── MarketEngine
Phase 2

Target:

MarketManager
├── MarketProvider
└── MarketEngine
Phase 3

Legacy implementation removed.

Only Target Architecture remains.

Migration Acceptance Criteria

Migration is considered complete when:

MarketProvider has no dependency on MarketEngine.
MarketProvider owns no detectors.
MarketProvider performs no market analysis.
MarketEngine owns all analysis and detector execution.
MarketManager coordinates both components.
Public API remains compatible.
All compile tests pass.
All unit tests pass.
All integration tests pass.
Architecture Rules

The following architecture rules shall always apply:

One owner per responsibility.
One public manager per module.
No circular dependencies.
No hidden ownership.
Business logic belongs inside engines only.
Providers supply data only.
Managers coordinate modules only.
Architecture Freeze Process

This architecture is frozen.

Any architectural modification requires:

Architecture Review.
Approved Change Request.
Architecture documentation update.
Dependency review.
Interface review.

No implementation may violate this architecture
after Sprint 1.x migration is complete.

Document Status

Document:

ARCHITECTURE_FREEZE.md

Status:

Approved Architecture Document

Architecture Baseline:

ABR-1.0

Review Phase:

Phase 0.3 — Foundation Architecture Review

Review Status:

Completed

End of ARCHITECTURE_FREEZE
