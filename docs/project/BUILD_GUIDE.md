# XAU AI PLATFORM Build Guide

Version : 1.0.0

Status : Foundation

Architecture Baseline : ABR-1.0

---

## Purpose

This document defines the standard build process for the XAU AI PLATFORM.

Every contributor must follow this guide to ensure consistent, reliable, and reproducible builds.

---

## Supported Platform

The project build environment supports:

- MetaTrader 5.
- MetaEditor.
- MQL5 Compiler.

---

## Build Configuration

The project supports the following build configurations:

- Debug.
- Release.

The project should compile successfully in both configurations whenever applicable.

---

## Build Requirements

MetaEditor compile scripts must preserve each source and log path as one
argument. Use embedded double quotes in both `/compile:` and `/log:` values so
Windows profile and workspace paths containing spaces are supported. The
focused regression check is `tests\TestCompileScriptPathQuoting.ps1`.

Before every build, verify:

- Project structure is valid.
- Include paths are correct.
- No missing dependencies exist.
- No duplicate files exist.
- No duplicate classes exist.

---

## Compiler Requirements

The project must compile with:

- Zero compile errors.
- Zero syntax errors.

Compiler warnings should be investigated and resolved whenever practical.

---

## Build Process

The standard build process is:

### Step 1: Open Project

Open the project in MetaEditor.

---

### Step 2: Verify Source Files

Verify that:

- Required source files exist.
- Include paths are valid.
- Dependencies are available.

---

### Step 3: Execute Build

Run the project build process using the MQL5 compiler.

---

### Step 4: Review Compiler Output

Review:

- Compile errors.
- Syntax errors.
- Warnings.
- Dependency issues.

---

### Step 5: Resolve Issues

Resolve all detected issues before continuing.

---

### Step 6: Rebuild

Repeat the build process until the project completes successfully.

---

## Dependency Validation

Before compilation verify:

- Include paths.
- Circular dependencies.
- Missing files.
- Duplicate includes.
- Dependency direction compliance.

---

## Output Validation

After a successful build verify:

- Executable output is generated successfully.
- No missing resources exist.
- No broken references exist.

---

## Logging Requirements

During development:

- Log important initialization events.
- Log major runtime errors.
- Avoid excessive logging in production environments.

---

## Build Failure Policy

If the build fails:

- Do not merge changes.
- Fix all compile errors.
- Rebuild the project.
- Revalidate the result.

A failed build must not be considered complete.

---

## Build Success Criteria

A successful build requires:

- Compilation completed successfully.
- No compile errors.
- No syntax errors.
- Project ready for testing.

---

## Document Review Status

Document:

BUILD_GUIDE.md

Review Phase:

Phase 0.3 — Foundation Architecture Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Next Review:

Build Process Audit

---

## Document Ownership

Owner:

XAU AI PLATFORM Architecture Team

Document Type:

Development Process Document

Maintained By:

Build Governance Process

Authority:

This document is governed by:

- ARCHITECTURE_FREEZE.md
- DEPENDENCY_RULES.md
- DOCUMENTATION_GOVERNANCE.md
- DEFINITION_OF_DONE.md

---

## Change History

| Version | Date | Change Description |
| --- | --- | --- |
| 1.0.0 | Phase 0.3 | Initial Build Guide created |

---
