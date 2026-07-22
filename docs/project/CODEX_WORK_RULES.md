# XAU AI PLATFORM — CODEX WORK RULES

Version : 1.0.0

Status : FROZEN

Architecture Baseline : ABR-1.0

---

## Purpose

This document defines the rules and limitations for Codex-assisted development within the XAU AI PLATFORM.

All automated code generation, modification, and documentation updates must follow these rules.

---

## General Rules

Codex shall:

* Follow the Coding Standard.
* Follow the Architecture Freeze.
* Follow the Dependency Rules.
* Preserve compile compatibility.
* Follow One Class Per File rule.
* Follow One Responsibility Per Class rule.

---

## Allowed Tasks

Codex may perform the following tasks:

* Create new files defined by the approved project plan.
* Generate class skeletons.
* Add required include directives.
* Fix include paths.
* Implement approved business logic.
* Refactor code according to approved specifications.
* Fix compilation errors caused by its own changes.
* Update project documentation when instructed.

---

## Forbidden Tasks

Codex must not perform the following tasks without approval:

* Change the architecture.
* Change module responsibilities.
* Create new modules without approval.
* Rename public classes without approval.
* Delete existing files without approval.
* Change public interfaces without approval.
* Add third-party libraries without approval.
* Introduce circular dependencies.
* Break layer rules.

---

## Working Procedure

Before modifying code:

1. Read the Coding Standard.
2. Read the Architecture Freeze.
3. Read the Dependency Rules.
4. Read the Module Interface Catalog.

---

## Implementation Procedure

During implementation:

* Modify only approved files.
* Keep changes as small as possible.
* Preserve existing formatting.
* Keep comments consistent.
* Avoid unrelated modifications.

After implementation:

* Verify include paths.
* Verify compile compatibility.
* Verify no layer violations.
* Update documentation when required.

---

## Output Requirements

When completing a task, Codex must report:

* Files modified.
* Files created.
* Summary of changes.
* Compile status.
* Remaining TODO items.

---

## Architecture Freeze Enforcement

If a requested change conflicts with the frozen architecture:

Codex must stop implementation.

The following actions are required:

* Report the architecture conflict.
* Identify affected components.
* Request Architecture Review.
* Wait for approved Change Request before continuing.

---

## Codex Compliance Rules

Codex output must remain consistent with:

* Project architecture.
* Coding standards.
* Dependency rules.
* Documentation governance.
* Approved implementation plans.

---

## Related Documents

This document shall be interpreted together with:

* ARCHITECTURE_FREEZE.md
* ARCHITECTURE_DECISIONS.md
* DEPENDENCY_RULES.md
* MODULE_INTERFACE_CATALOG.md
* docs/standards/Coding_Standard.md
* DOCUMENTATION_GOVERNANCE.md

---

## Document Review Status

Document:

CODEX_WORK_RULES.md

Review Phase:

Phase 0.3 — Foundation Architecture Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Next Review:

Codex Governance Audit

---

## Document Ownership

Owner:

XAU AI PLATFORM Architecture Team

Document Type:

Codex Governance Document

Maintained By:

Codex Development Governance Process

Authority:

This document is governed by:

* ARCHITECTURE_FREEZE.md
* ARCHITECTURE_DECISIONS.md
* DOCUMENTATION_GOVERNANCE.md
* docs/standards/Coding_Standard.md

---

## Change History

| Version | Date      | Change Description               |
| ------- | --------- | -------------------------------- |
| 1.0.0   | Phase 0.3 | Initial Codex Work Rules created |

---
