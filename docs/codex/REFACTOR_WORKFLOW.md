# XAU AI PLATFORM - Codex Refactor Workflow

Version: 1.0.0

Status: Standard

---

## Purpose

This document defines the standard refactoring workflow.

The goal is to improve code quality without changing system behavior.

---

## Refactoring Rules

Refactoring must:

- Preserve functionality.
- Preserve interfaces.
- Reduce technical debt.
- Improve maintainability.

---

## Allowed Refactoring

Examples:

- Code cleanup.
- Duplicate code reduction.
- Naming improvement.
- Internal structure improvement.
- Performance improvement without behavior change.

---

## Restricted Changes

The following require review:

- Interface changes.
- Module boundary changes.
- Dependency changes.
- Architecture changes.

---

## Refactoring Process

### Step 1

Identify refactoring reason.

### Step 2

Analyze impact.

### Step 3

Apply minimal changes.

### Step 4

Verify:

- Build.
- Tests.
- Dependency rules.

---

## Refactor Report

Codex must provide:

- Reason for Refactor.
- Files Changed.
- Impact Analysis.
- Verification Result.
