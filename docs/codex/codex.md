# XAU-AI-PLATFORM Codex Audit Guide

Version: 1.0.0

Status: Audit Standard

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the audit rules and validation procedures for Codex when reviewing the XAU-AI-PLATFORM repository.

The purpose is to ensure that all implementation changes remain consistent with the approved architecture.

Codex must use this document together with the Architecture Decision Records (ADR).

---

## Audit Authority

The following documents are the source of truth:

```text
docs/Architecture.md

docs/architecture/adr/ADR-001_Canonical_Runtime_Path.md

docs/architecture/adr/ADR-002_Module_Dependency_Direction.md

docs/architecture/adr/ADR-003_Risk_Boundary.md

docs/architecture/adr/ADR-004_Execution_Ownership.md
```

All audit findings must reference these documents.

---

## Codex Role

Codex is responsible for:

* Repository analysis
* Architecture compliance checking
* Dependency inspection
* Boundary validation
* Finding documentation

Codex must not:

* Change architecture decisions
* Create new runtime paths
* Modify code without approval
* Introduce duplicate modules

---

## Audit Rules

## Rule 1 — Canonical Runtime Path

Verify that production execution follows:

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

Any alternative production path is a finding.

---

## Rule 2 — Dependency Direction

All dependencies must follow:

```text
Upper Layer

↓

Lower Layer
```

Forbidden:

```text
A

↓

B

↓

A
```

Circular dependency is an architecture violation.

---

## Rule 3 — Module Responsibility Boundary

Validate:

### Brain

Allowed:

* Market context analysis
* Signal analysis
* Decision proposal

Not allowed:

* Risk approval
* Position sizing
* Order execution

---

### Risk

Allowed:

* Risk validation
* Position sizing
* Exposure control
* Trade approval

Not allowed:

* Market interpretation
* Order submission

---

### Execution

Allowed:

* Trade request creation
* Validation
* Broker communication
* Order execution

Not allowed:

* Decision generation
* Market analysis
* Risk calculation

---

## Rule 4 — Execution Completeness

Verify:

```text
Decision

↓

Risk Approval

↓

Execution Pipeline

↓

Trade Executor

↓

Trade Lifecycle
```

Finding required when:

* Execution ends at result object only
* Trade Executor is unreachable
* Order path bypasses Risk

---

## Finding Classification

All findings must be classified:

### A — Architecture Breaking

Examples:

* Multiple runtime paths
* Invalid architecture flow
* Missing critical ownership

---

### B — Boundary Violation

Examples:

* Brain owns Risk
* Execution owns Decision
* Risk owns Broker Operation

---

### C — Dependency Violation

Examples:

* Circular dependency
* Reverse include dependency
* Layer violation

---

### D — Documentation / Minor

Examples:

* Empty documents
* Formatting issues
* Outdated references
* Missing comments

---

## Audit Output Format

Codex findings must use:

```text
Finding:

Location:

Severity:

Category:

Reason:

Architecture Reference:

Recommended Correction:
```

---

## Change Control

Before Architecture Freeze:

Codex must only report findings.

Code modification requires explicit approval.

After Architecture Freeze:

All changes must follow:

* Architecture Decision Records
* Module ownership rules
* Dependency rules

---

## Audit Status

```text
Codex Audit Guide: ACTIVE

Architecture Baseline: ABR-1.0
```
