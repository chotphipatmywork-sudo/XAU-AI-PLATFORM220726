# XAU AI PLATFORM - Codex Bug Fix Workflow

Version: 1.0.0

Status: Standard

---

## Purpose

This document defines the standard workflow for fixing defects in the XAU AI PLATFORM.

The objective is to ensure every bug fix is controlled, traceable, and verified.

---

## Bug Fix Principles

All bug fixes must:

- Preserve architecture rules.
- Follow coding standards.
- Avoid unnecessary changes.
- Maintain module boundaries.
- Include verification results.

---

## Bug Fix Process

### Step 1 - Issue Identification

Record:

- Error message.
- File location.
- Module affected.
- Expected behavior.
- Actual behavior.

---

### Step 2 - Root Cause Analysis

Before modifying code:

- Identify root cause.
- Check dependencies.
- Check interface impact.
- Confirm affected scope.

---

### Step 3 - Implementation

Codex may:

- Modify affected files.
- Add required tests.
- Update documentation if required.

Codex must not:

- Redesign architecture.
- Change public interfaces without approval.
- Add unrelated improvements.

---

### Step 4 - Verification

Required checks:

- Compilation result.
- Test result.
- Dependency verification.
- Review checklist.

---

## Bug Fix Report

Codex must provide:

- Issue Summary
- Root Cause
- Files Modified
- Changes Made
- Verification Result
- Remaining Risks

---

## Approval

Major changes require architecture review before merging.
