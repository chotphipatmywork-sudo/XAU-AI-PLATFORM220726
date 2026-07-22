# XAU AI PLATFORM — MODULE API GUIDELINES

Version: 1.0.0

Status: Foundation Standard

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the public API guidelines
for every module within the XAU AI PLATFORM.

The objective is to ensure that all modules expose:

* Consistent interfaces.
* Maintainable contracts.
* Architecture-safe communication.
* Stable public boundaries.

---

## API Design Principles

Every public API shall:

* Have a single responsibility.
* Expose business capabilities only.
* Hide implementation details.
* Remain stable after publication.

A public API represents a long-term
architecture contract.

---

## Public API Requirements

Every module shall expose:

* One primary interface.
* Clearly defined responsibilities.
* Stable method signatures.
* Well-defined ownership.

Implementation classes shall remain internal.

---

## Interface Visibility

Public API:

```text id="w3g8pq"
Public Interface
```

Internal implementation:

```text id="7q9k2s"
Implementation Classes

Internal Helpers

Private Utilities
```

Only approved public interfaces may be referenced
by external modules.

---

## Method Naming

Methods shall use clear action verbs.

Examples:

```cpp id="f4q8mn"
Initialize()

Analyze()

Validate()

Execute()

Shutdown()

Reset()
```

Avoid unclear generic names:

```text id="x2c9vb"
Run()

Do()

Process()

Handle()

Work()
```

Method names must describe
the responsibility being performed.

---

## Return Types

Public methods should return:

* Domain models.
* Result objects.
* Status values.

Avoid exposing:

* Internal classes.
* Temporary objects.
* Module implementation details.

Public return types are considered
stable contracts.

---

## Parameter Rules

Public methods should:

* Accept only required parameters.
* Avoid long parameter lists.
* Use domain models when appropriate.

Preferred:

```cpp id="r7m3pa"
Validate(OrderRequest)
```

Avoid:

```cpp id="n5w8kd"
Validate(
symbol,
volume,
price,
risk,
sl,
tp,
comment,
magic
)
```

Complex input data should be represented
by a defined domain model.

---

## Error Handling

Public APIs shall:

* Return predictable results.
* Report failures consistently.
* Avoid unexpected side effects.

Errors must not expose internal
implementation details.

Failure information should remain
understandable and traceable.

---

## Dependency Rules

A public API:

* Shall not depend on implementation classes.
* Shall not expose private objects.
* Shall not bypass architecture boundaries.

All communication shall follow
approved dependency rules.

Public APIs must respect:

* Layer boundaries.
* Package ownership.
* Dependency direction.

---

## API Stability

After publication:

* Method names remain stable.
* Parameter meanings remain stable.
* Return contracts remain stable.

Breaking changes require:

* Architecture review.
* Impact analysis.
* Approval before implementation.

---

## API Review Checklist

Before publishing an API:

| Check Item                | Required |
| ------------------------- | -------- |
| Interface defined         | Yes      |
| Single responsibility     | Yes      |
| Business-oriented methods | Yes      |
| Stable contract           | Yes      |
| Ownership defined         | Yes      |

---

## Related Documents

* INTERFACE_NAMING_STANDARD.md
* INTERFACE_CHANGE_POLICY.md
* MODULE_COMMUNICATION_STANDARD.md
* DEPENDENCY_RULES.md
* DOCUMENTATION_GOVERNANCE.md

---

## Document Status

Document:

`MODULE_API_GUIDELINES.md`

Document Type:

Development Standard Document

Review Phase:

Phase 0.3 — Foundation Standards Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Document Status:

Approved Module API Guidelines

---

End of MODULE_API_GUIDELINES.md
