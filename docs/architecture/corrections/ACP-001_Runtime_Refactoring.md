# ACP-001 Runtime Refactoring

Version: 1.0.0

Status: Draft

Architecture Baseline: ABR-1.0

---

## Purpose

This Architecture Correction Plan defines the required refactoring activities for establishing the canonical production runtime defined by ABR-1.0.

The objective is to remove conflicting runtime ownership and ensure that all production execution follows the approved architecture before Architecture Freeze.

---

## Related Findings

### Codex Architecture Compliance Audit Round 2

| Finding   | Severity | Description                                     |
| --------- | -------- | ----------------------------------------------- |
| Finding 1 | A        | Production entry bypasses Kernel                |
| Finding 2 | A        | Runtime does not execute the canonical pipeline |
| Finding 8 | A        | Alternative runtime paths remain                |

---

## Related Architecture Decisions

* ADR-001 Canonical Runtime Path
* ADR-002 Module Dependency Direction

---

## Objective

Establish one and only one production runtime path.

Approved runtime:

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

---

## Current State

Current implementation contains multiple runtime controllers.

Examples include:

```text
CCore

CRuntimeManager

CCoreEngine

CAIApplication

CSystemManager

CKernel
```

Production startup currently initializes `CCore`, bypassing the Kernel ownership defined by ADR-001.

Runtime context propagation is incomplete because the Runtime context is not initialized before pipeline execution.

---

## Target State

The production runtime shall contain:

```text
XAU-AI-PLATFORM.mq5

↓

CKernel

↓

CRuntime

↓

Business Pipeline
```

Only one runtime controller may exist in the production execution path.

Legacy controllers may remain temporarily only if they are completely isolated from production execution.

---

## Root Cause Analysis

The repository evolved through multiple architecture iterations.

Earlier runtime implementations remain in the source tree.

Responsibilities became duplicated across several runtime controllers, resulting in:

* Multiple lifecycle owners
* Inconsistent startup logic
* Duplicate initialization
* Incomplete pipeline execution

---

## Files Expected To Be Modified

The following files are expected to require implementation changes.

Production Entry:

```text
XAU-AI-PLATFORM.mq5
```

Kernel:

```text
core/kernel/
```

Runtime:

```text
core/runtime/
```

Legacy Runtime Controllers:

```text
core/Core.mqh

core/core/

core/application/

core/system/
```

Actual implementation changes shall be confirmed before modification.

---

## Refactoring Strategy

### Step 1

Redirect production startup to Kernel.

Expected result:

```text
EA

↓

Kernel
```

---

### Step 2

Assign Kernel as the only runtime owner.

Kernel initializes:

* Runtime
* Module Registry
* Required services

---

### Step 3

Move runtime context initialization into Runtime.

Runtime shall receive:

* Symbol
* Timeframe
* Tick context

before executing the business pipeline.

---

### Step 4

Execute the canonical pipeline.

Required execution order:

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

---

### Step 5

Isolate legacy runtime controllers.

Legacy components shall not participate in production execution.

---

## Risks

Potential implementation risks include:

* Startup regression
* Initialization order changes
* Hidden runtime dependencies
* Legacy include dependencies

Each change shall be verified before proceeding to the next step.

---

## Validation Criteria

This correction is complete when:

* Production entry reaches Kernel
* Kernel owns Runtime
* Runtime initializes context
* Canonical pipeline executes in order
* No alternative runtime path is active
* Codex Architecture Audit reports no Finding 1
* Codex Architecture Audit reports no Finding 2
* Codex Architecture Audit reports no Finding 8

---

## Completion Checklist

| Item                           | Status |
| ------------------------------ | ------ |
| Runtime ownership defined      | ☐      |
| Production entry updated       | ☐      |
| Runtime context initialized    | ☐      |
| Canonical pipeline implemented | ☐      |
| Legacy runtime isolated        | ☐      |
| Codex verification passed      | ☐      |
| ACP approved                   | ☐      |

---

## Exit Criteria

ACP-001 may be closed only when all validation criteria are satisfied and the related Architecture Breaking findings have been resolved.
