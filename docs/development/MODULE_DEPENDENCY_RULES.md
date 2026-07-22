# XAU AI PLATFORM — MODULE DEPENDENCY RULES

Version: 1.0.0

Status: Foundation Standard

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines dependency rules between modules within the XAU AI PLATFORM.

The objective is to ensure:

- Stable architecture boundaries.
- Predictable module communication.
- Controlled coupling.
- Prevention of circular dependencies.

Dependency rules are mandatory architecture constraints.

---

## Dependency Principles

Every module dependency shall:

- Be explicit.
- Have clear ownership.
- Follow architecture direction.
- Use approved interfaces.
- Remain documented.

Hidden dependencies are prohibited.

---

## Dependency Direction

Module dependencies shall follow:

```text
Higher Layer

↓

Lower Layer

Allowed:

Application

↓

Runtime

↓

Module

↓

Service

↓

Model

Dependencies must not flow upward.

Layer Dependency Model

The standard dependency direction is:

Application Layer

↓

Runtime Layer

↓

Domain Module Layer

↓

Service Layer

↓

Model Layer

Each layer may depend only on approved lower layers.

Module Boundary Rule

Each module must have:

Defined responsibility.
Public contract.
Internal implementation boundary.
Ownership definition.

External modules shall access only public contracts.

Public Dependency Rule

Allowed:

Module A

↓

Public Interface

↓

Module B

Not allowed:

Module A

↓

Internal Class

↓

Module B

Internal implementation must remain private.

Interface Dependency

Modules shall communicate through:

Public interfaces.
Stable result objects.
Documented contracts.

Direct dependency on implementation classes is prohibited.

Allowed Dependencies

A module may depend on another module only when:

Responsibility is clearly separated.
Dependency direction is valid.
Public contract exists.
Ownership is defined.

Example:

Brain

↓

Market Interface

↓

Market Module

The dependency must represent a valid business relationship.

Forbidden Dependencies

The following dependencies are prohibited.

Reverse Dependency

Example:

Lower Layer

↑

Higher Layer

Reason:

Creates architecture instability.

Circular Dependency

Example:

Module A

↓

Module B

↓

Module A

Circular dependency is prohibited.

Each dependency graph must remain acyclic.

Hidden Dependency

Example:

Module A

↓

Internal Implementation

↓

Module B

Modules must not bypass public boundaries.

Cross Module Dependency Rules

Cross module communication shall:

Use approved interfaces.
Use documented models.
Preserve ownership.
Avoid direct state access.

A module must not modify another module's internal state.

Dependency Ownership

Each dependency shall define:

Item    Requirement
Source Module   Required
Target Module   Required
Interface Used  Required
Reason  Required
Owner Approval  Required
Dependency Documentation

Every important dependency must be documented.

Documentation should include:

Dependency purpose.
Communication method.
Data exchanged.
Impact analysis.

Undocumented dependencies are not allowed.

Dependency Change Rules

Changing dependencies requires:

Architecture review.
Impact analysis.
Documentation update.
Validation.

Dependency changes may affect multiple modules.

Dependency Review Process

Before adding a dependency:

Request

↓

Architecture Review

↓

Approval

↓

Implementation

↓

Validation

No dependency shall be added without review.

Dependency Examples
Valid Dependency
AI Runtime

↓

Brain Interface

↓

Brain Module

Reason:

Communication uses contract.
Dependency direction is correct.
Ownership is clear.
Invalid Dependency
Model

↓

Execution Engine

Reason:

Model should not know business layer.
Creates reverse dependency.
Invalid Direct Access
Execution Module

↓

Brain Internal Analyzer

Reason:

Bypasses public interface.
Violates module boundary.
Dependency Graph Rules

The complete dependency graph shall:

Have one clear direction.
Contain no cycles.
Preserve module isolation.
Allow independent testing.

Example:

Market

↓

Brain

↓

AI Runtime

↓

Risk

↓

Execution

↓

Trade Lifecycle
Dependency Review Checklist

Before approving a module dependency:

Check Item  Required
Dependency direction correct    Yes
Public interface used   Yes
Ownership defined   Yes
No circular dependency  Yes
Documentation updated   Yes
Architecture approved   Yes
Module Dependency Iron Rules
Rule 1

Never depend on internal implementation.

Rule 2

Never create reverse dependency.

Rule 3

Never create circular dependency.

Rule 4

Every dependency must have an owner.

Rule 5

Every communication must use approved contracts.

Rule 6

Architecture boundary must always be preserved.

Related Documents
ARCHITECTURE_FREEZE.md
ARCHITECTURE_DECISIONS.md
MODULE_INTERFACE_CATALOG.md
MODULE_COMMUNICATION_STANDARD.md
MODULE_API_GUIDELINES.md
INTERFACE_CHANGE_POLICY.md
DEFINITION_OF_DONE.md
Document Status

Document:

MODULE_DEPENDENCY_RULES.md

Document Type:

Development Standard Document

Review Phase:

Phase 0.3 — Foundation Governance Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

End of MODULE_DEPENDENCY_RULES.md
