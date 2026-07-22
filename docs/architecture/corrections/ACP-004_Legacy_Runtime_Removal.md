# ACP-004 Legacy Runtime Removal

Version: 1.0.0

Status: Draft

Architecture Baseline: ABR-1.0

---

## Purpose

This Architecture Correction Plan defines the activities required to eliminate legacy runtime paths from the production architecture.

The objective is to ensure that only the approved canonical runtime remains active in production while preserving legacy components only for temporary migration or historical reference where necessary.

---

## Related Findings

### Codex Architecture Compliance Audit Round 2

| Finding   | Severity | Description                           |
| --------- | -------- | ------------------------------------- |
| Finding 8 | A        | Alternative runtime paths remain      |
| Finding 9 | D        | Duplicate runtime ownership artifacts |

---

## Related Architecture Decisions

* ADR-001 Canonical Runtime Path
* ADR-002 Module Dependency Direction

---

## Objective

Ensure that the production system contains a single runtime implementation.

Approved production runtime:

```text
XAU-AI-PLATFORM.mq5

↓

Kernel

↓

Runtime

↓

Business Pipeline
```

No alternative runtime controller shall participate in production execution.

---

## Current State

The repository still contains multiple runtime-related controllers originating from earlier architecture iterations.

Examples include:

```text
CCore

CCoreEngine

CAIApplication

CSystemManager

CApplication

Legacy Module Registry
```

Several of these components duplicate runtime ownership or startup responsibilities.

Although some are incomplete, their continued presence increases architectural ambiguity.

---

## Target State

Production startup shall be controlled exclusively by:

```text
Kernel

↓

Runtime
```

Legacy runtime components shall satisfy one of the following conditions:

* Removed from production.
* Isolated from production builds.
* Clearly marked as deprecated.
* Retained only for controlled migration.

No legacy runtime shall be reachable from the production entry point.

---

## Root Cause Analysis

The runtime architecture evolved through several implementation stages.

Earlier runtime controllers were retained while new architecture layers were introduced.

This resulted in:

* Duplicate runtime ownership
* Conflicting startup flows
* Multiple controller implementations
* Increased maintenance complexity

---

## Files Expected To Be Reviewed

Potential review targets include:

```text
core/

core/core/

core/application/

core/system/

core/kernel/
```

Final implementation targets shall be confirmed before modification.

---

## Refactoring Strategy

### Step 1

Identify all runtime controllers.

---

### Step 2

Classify each controller as:

* Production
* Migration
* Deprecated
* Remove

---

### Step 3

Disconnect legacy controllers from production startup.

---

### Step 4

Remove duplicate runtime ownership.

---

### Step 5

Retain only one production startup path.

---

### Step 6

Document all deprecated runtime components.

---

## Risks

Potential implementation risks include:

* Hidden compile dependencies
* Legacy include chains
* Startup regressions
* Historical compatibility requirements

All removals shall be validated incrementally.

---

## Validation Criteria

This correction is complete when:

* Only one production runtime exists.
* Kernel owns production startup.
* No legacy runtime is reachable from the production entry point.
* Duplicate runtime ownership has been eliminated.
* Deprecated components are documented.
* Codex reports no Finding 8.
* Codex reports no unresolved runtime ownership conflicts.

---

## Completion Checklist

| Item                             | Status |
| -------------------------------- | ------ |
| Runtime controllers identified   | ☐      |
| Legacy controllers classified    | ☐      |
| Production startup isolated      | ☐      |
| Duplicate ownership removed      | ☐      |
| Deprecated components documented | ☐      |
| Codex verification passed        | ☐      |
| ACP approved                     | ☐      |

---

## Exit Criteria

ACP-004 may be closed only after the production runtime has been consolidated into the canonical architecture and all legacy runtime paths have been removed or fully isolated from production execution.
