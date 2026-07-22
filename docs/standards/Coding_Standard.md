# XAU AI PLATFORM — CODING STANDARD

Version: 1.0.0

Status: Foundation Standard

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines implementation coding standards
for the XAU AI PLATFORM project.

The objective is to ensure:

* Consistent source code structure.
* Maintainable implementation.
* Clear responsibility separation.
* Stable development workflow.

---

## General Coding Rules

All source code must follow:

* One Class Per File.
* One Responsibility Per Class.
* One Responsibility Per Function.
* Clear naming convention.
* Explicit dependency usage.

---

## File Structure Rules

Every source file should contain:

```text
Header

Includes

Class Definition

Implementation

End of File
```

Source files must have a clear responsibility.

A file must not contain unrelated functionality.

---

## File Header Standard

Every source file should begin with:

```cpp
//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : FileName.mqh                                           |
//| Layer   : Layer Name                                             |
//| Version : x.x.x                                                  |
//| Purpose : Description                                             |
//+------------------------------------------------------------------+
```

---

## Include Rules

Include order must follow:

1. Config.
2. Models.
3. Interfaces.
4. Engines.
5. Services.
6. Assemblers.

Rules:

* Include only required files.
* Avoid unnecessary dependencies.
* Avoid circular dependency.

---

## Class Naming Convention

Classes must use PascalCase.

Examples:

```cpp
CTrendAnalyzer

CTrendEngine

CRiskManager
```

All class names must begin with:

```text
C
```

---

## Variable Naming Convention

Member variables:

```cpp
m_config

m_engine

m_result
```

Local variables:

```cpp
result

context

workspace
```

Rules:

* Names must describe purpose.
* Avoid unclear abbreviations.
* Prefer readability over short names.

---

## Function Naming Convention

Functions must use PascalCase.

Examples:

```cpp
Analyze()

Calculate()

Execute()

Reset()

Initialize()
```

Function names must describe actions clearly.

---

## Function Size Rules

Recommended size:

```text
20 - 50 lines
```

Maximum size:

```text
100 lines
```

Large functions must be separated into smaller functions.

---

## Comment Rules

Comments must explain:

```text
WHY
```

not:

```text
WHAT
```

Bad:

```cpp
// Increase counter
counter++;
```

Good:

```cpp
// Skip invalid market state
counter++;
```

---

## Error Handling Rules

Every module must:

* Validate input.
* Handle invalid state.
* Return clear result.
* Avoid silent failure.

Errors must be traceable.

---

## Memory Rules

Code must:

* Avoid unnecessary object creation.
* Release resources correctly.
* Avoid memory duplication.

---

## Compile Rules

Every new or modified file must:

* Compile successfully.
* Resolve dependencies.
* Pass validation.

before moving to the next development step.

---

## Review Rules

Before merging code:

Required:

* Architecture compliance.
* Coding standard compliance.
* Dependency review.
* Compile validation.

---

## Coding Standard Checklist

| Check Item                | Status   |
| ------------------------- | -------- |
| One Class Per File        | Required |
| Naming Convention Correct | Required |
| Dependency Correct        | Required |
| Compile Passed            | Required |
| No Duplicate Logic        | Required |

---

## Document Status

Document:

`Coding_Standard.md`

Document Type:

Development Standard Document

Review Phase:

Phase 0.3 — Foundation Standards Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Document Status:

Approved Coding Standard

---

End of Coding_Standard.md
