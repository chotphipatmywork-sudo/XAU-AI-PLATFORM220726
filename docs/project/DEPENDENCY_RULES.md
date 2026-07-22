# XAU AI PLATFORM — Dependency Rules

Version : 1.1.0

Status : Foundation

Architecture Baseline : ABR-1.0

---

## Purpose

This document defines the dependency rules for the entire
XAU AI PLATFORM.

Every module, package, and source file must follow these rules.

The objectives are:

- Maintain controlled architecture.
- Prevent unwanted coupling.
- Preserve module boundaries.
- Ensure scalable development.
- Protect public interface contracts.

This document defines:

- Dependency direction.
- Allowed dependencies.
- Forbidden dependencies.
- Public interface dependency rules.
- Dependency change control.

---

## Dependency Principles

Every dependency must be:

- Explicit.
- Documented.
- Traceable.
- Reviewable.

The following dependency patterns are prohibited:

- Hidden dependencies.
- Circular dependencies.
- Reverse dependencies.
- Direct internal implementation access.

---

## Dependency Direction

All dependencies must follow the approved architecture direction.

The dependency flow is:

```text
Runtime

    ↓

Market

    ↓

Context

    ↓

Brain

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

A lower layer must never reference a higher layer.

Dependency Ownership Rules

Each module owns its internal implementation.

External modules may access only:

Public interfaces.
Approved shared contracts.
Documented communication points.

External modules must not access:

Internal classes.
Private engines.
Internal services.
Internal providers.
Private models.
Internal state.
Allowed Dependencies
Runtime Module

Allowed dependencies:

Common Module.
Config Module.
Logging Module.

Responsibilities:

Application lifecycle.
Event processing.
Runtime coordination.
Market Module

Allowed dependencies:

Runtime Module.
Data Module.
Common Module.
Config Module.
Logging Module.

Responsibilities:

Market data access.
Market context preparation.

Market Module must not contain:

Trading decisions.
Risk logic.
Execution logic.
Context Module

Allowed dependencies:

Market Module.
Common Module.
Shared Models.

Responsibilities:

Context aggregation.
Information preparation.

Context Module does not perform decisions.

Brain Module

Allowed dependencies:

Context Module.
Shared Models.

Responsibilities:

Market reasoning.
Context interpretation.
Analysis generation.

Brain Module must not access:

Execution APIs.
Order management.
Trading operations.
Decision Module

Allowed dependencies:

Brain Module.
Shared Models.

Responsibilities:

Convert analysis results into decisions.

Decision Module must not:

Execute trades.
Access order systems.
Risk Module

Allowed dependencies:

Decision Module.
Money Module.
Position Module.
Shared Models.

Responsibilities:

Risk validation.
Exposure control.
Trade approval.

Risk Module must not:

Generate signals.
Execute orders directly.
Execution Module

Allowed dependencies:

Risk Module.
Money Module.
Position Module.
Infrastructure Module.
Shared Models.

Responsibilities:

Order preparation.
Order submission.
Execution reporting.

Execution Module must not:

Analyze market conditions.
Generate decisions.
Access learning logic.
Trade Lifecycle Module

Allowed dependencies:

Execution Module.
Position Module.
Risk Module.

Responsibilities:

Trade state management.
Entry and exit lifecycle.
Portfolio Module

Allowed dependencies:

Position Module.
Trade Lifecycle Module.

Responsibilities:

Account state.
Performance tracking.
Exposure summary.
Learning Module

Allowed dependencies:

Portfolio Module.
Trade Lifecycle Module.
Market Module.

Responsibilities:

Model improvement.
Historical evaluation.
Learning feedback.

Learning Module must not:

Execute trades.
Override risk controls.
Forbidden Dependencies
Reverse Dependency

Example:

Risk

↓

Decision

Not allowed.

Reason:

Lower control layers must not control higher reasoning layers.

Circular Dependency

Example:

Market

↓

Brain

↓

Market

Not allowed.

Reason:

Creates unstable ownership and unpredictable behavior.

Cross Layer Shortcut

Example:

Execution

↓

Market

Not allowed.

Execution must receive approved information through defined contracts.

Direct Internal Access

External modules must not access:

Internal engines.
Internal assemblers.
Private implementations.
Hidden state.

Only public interfaces are allowed.

Public Interface Dependency Rules

The dependency model is:

External Module

        ↓

Public Interface

        ↓

Module Implementation

        ↓

Private Components

Rules:

Consumers depend on interfaces.
Implementations remain replaceable.
Ownership remains inside the module.
Public contracts remain stable.
Dependency Change Process

Any dependency modification requires:

Dependency impact analysis.
Architecture review.
Approval.
Implementation.
Compile validation.
Documentation update.
Architecture freeze update when required.
Dependency Violation Handling

If a dependency violation is discovered:

The issue must be:

Identified.
Documented.
Reviewed.
Corrected.

Examples:

Reverse dependency.
Circular dependency.
Interface bypass.
Hidden coupling.
Unauthorized module access.
Related Documents

This document must be interpreted together with:

PROJECT_CONSTITUTION.md
ARCHITECTURE_PRINCIPLES.md
ARCHITECTURE_DECISIONS.md
ARCHITECTURE_FREEZE.md
MODULE_INTERFACE_CATALOG.md
Dependency Rules Summary

Every implementation must follow:

Dependency flows downward only.
Reverse dependency is prohibited.
Circular dependency is prohibited.
Cross-layer shortcuts are prohibited.
Hidden dependencies are prohibited.
Public interfaces are the only integration points.
Dependency changes require review.
Architecture Freeze

This document is part of the Architecture Baseline.

After Architecture Freeze:

Dependency direction is frozen.
Module relationships are frozen.
Public dependency contracts are frozen.

Any modification requires:

Approved Change Request.
Architecture Review.
Documentation Update.
Document Review Status

Document:

DEPENDENCY_RULES.md

Review Phase:

Phase 0.3 — Foundation Architecture Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Next Review:

Module Interface Catalog Review

Document Ownership

Owner:

XAU AI PLATFORM Architecture Team

Document Type:

Architecture Governance Document

Maintained By:

Architecture Dependency Governance Process

Authority:

Governed by:

ARCHITECTURE_FREEZE.md
ARCHITECTURE_DECISIONS.md
DOCUMENTATION_GOVERNANCE.md
Change History
Version Date Change Description
1.0.0 Initial Initial dependency rules created
1.1.0 Phase 0.3 Updated dependency governance and architecture alignment
