# XAU AI PLATFORM - Coding Standard

Version: 1.0.0

Status: Foundation

Architecture Baseline: Pre-ABR-1.0

---

## Purpose

This document defines the coding standard for the entire XAU AI PLATFORM.

Every source file must follow this standard.

The objective is to maintain:

* Consistent code structure
* Clear responsibility boundaries
* Stable architecture evolution
* Safe collaboration between Human Developer and Codex

---

## General Rules

### File Responsibility

Every source file must follow:

* One Class Per File
* One Responsibility Per Class
* One Responsibility Per Function

Each component must have a clear purpose and avoid mixing unrelated responsibilities.

---

## File Header Standard

Every source file must begin with the following header format:

```cpp
//+------------------------------------------------------------------+
//| Project : XAU AI PLATFORM                                        |
//| File    : FileName.mqh                                           |
//| Layer   : Layer Name                                             |
//| Version : x.x.x                                                  |
//| Purpose : Description                                             |
//+------------------------------------------------------------------+
```

The header must identify:

* Project
* File name
* Architecture layer
* Version
* Purpose

---

## Include Rule

Include order must follow:

1. Config
2. Models
3. Engines
4. Services
5. Assemblers

Example order:

```text
Config

↓

Models

↓

Engines

↓

Services

↓

Assemblers
```

Rules:

* Never include unnecessary files.
* Avoid circular dependencies.
* Follow layer dependency rules.

---

## Class Naming Standard

Classes must use PascalCase.

Examples:

```text
CTrendAnalyzer

CTrendAssembler

CEMAEngine
```

Rules:

* Every class name must begin with:

```text
C
```

* Class names must describe responsibility clearly.

---

## Variable Naming Standard

### Member Variables

Use prefix:

```text
m_
```

Examples:

```text
m_config

m_engine

m_workspace
```

---

### Local Variables

Use descriptive names:

Examples:

```text
result

context

workspace
```

Rules:

* Avoid unclear abbreviations.
* Prioritize readability.

---

## Function Naming Standard

Functions must use PascalCase.

Examples:

```text
Analyze()

Assemble()

Calculate()

Reset()

SetConfig()
```

Function names must describe the action performed.

---

## Function Size Standard

Recommended function size:

```text
20 - 50 lines
```

Maximum:

```text
100 lines
```

If a function exceeds the limit:

* Split responsibilities.
* Create helper functions.
* Maintain single responsibility.

---

## Comment Standard

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
// Increase i
i++;
```

Good:

```cpp
// Skip invalid candle
i++;
```

Comments should explain design decisions or reasoning.

---

## Architecture Coding Rule

The architecture flow must follow:

```text
Business Logic

↓

Engine

↓

Aggregation

↓

Assembler

↓

Workflow

↓

Analyzer

↓

Package Result
```

Rules:

* Business Logic must not be mixed with infrastructure.
* Assemblers must not contain decision logic.
* Analyzer coordinates workflow only.

---

## Compile Rule

Every new file:

* Must compile successfully.
* Must pass validation.
* Must be reviewed before moving to the next implementation step.

No incomplete file should enter the next phase.

---

## Documentation Rule

Every architectural decision must be documented before implementation.

Required documentation includes:

* Purpose
* Reason
* Impact
* Dependency consideration

---

## Iron Rules

The following rules are permanent architecture constraints.

### Dependency Rules

1. Never break Layer Dependency.

2. Never place Business Logic inside Workspace.

3. Never place Indicator Logic inside Assembler.

---

### Responsibility Rules

1. Analyzer is only Orchestrator.

2. Every Package returns one Result object.

3. Every file must compile individually.

---

### Development Order

1. Architecture first.

2. Logic second.

---

## End of Standard

This coding standard is the baseline reference for all XAU AI PLATFORM development.
