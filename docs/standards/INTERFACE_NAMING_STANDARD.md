# XAU AI PLATFORM — INTERFACE NAMING STANDARD

Version: 1.0.0

Status: Foundation Standard

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the interface naming standard
used throughout the XAU AI PLATFORM.

The objective is to establish:

* Consistent naming convention.
* Predictable interface structure.
* Maintainable architecture contracts.

This standard applies to every interface
defined within the project.

---

## Naming Principles

Interface names shall:

* Clearly describe responsibility.
* Represent a single capability.
* Avoid implementation details.
* Remain stable over time.

Every interface is considered
an architecture contract.

Interface naming must communicate
ownership and purpose clearly.

---

## Interface Boundary

Interface communication shall follow:

```text id="z8y7ke"
External Module

        |

        v

Public Interface

        |

        v

Internal Implementation
```

External modules shall depend only
on approved interfaces.

Implementation details must remain hidden.

---

## General Naming Convention

All interfaces shall begin with the prefix:

```text id="5j4b5r"
I
```

Format:

```text id="4r7h2m"
I<Responsibility><Role>
```

Examples:

```text id="8u2l9c"
IMarketProvider

IBrainAnalyzer

IRiskValidator

IExecutionProvider

IPositionProvider

IPortfolioProvider
```

Interface names must describe capability
rather than technical implementation.

---

## Approved Role Suffixes

The following suffixes are approved:

| Suffix     | Purpose                          |
| ---------- | -------------------------------- |
| Provider   | Supplies information             |
| Analyzer   | Performs analysis                |
| Validator  | Performs validation              |
| Manager    | Coordinates operations           |
| Factory    | Creates objects                  |
| Repository | Provides persistent storage      |
| Strategy   | Defines interchangeable behavior |
| Service    | Provides reusable functionality  |

Only approved suffixes should be used
for public interfaces.

---

## Naming Examples

Good examples:

```text id="n8w2s3"
IMarketProvider

IDataProvider

IAIDecisionProvider

ILearningProvider
```

Bad examples:

```text id="m1j8r6"
IData

IEngine

IHelper

IManager

ITest
```

Reason:

The interface responsibility is unclear.

---

## Single Responsibility Rule

Each interface shall expose
one responsibility only.

Good:

```text id="6p9kq1"
IRiskValidator
```

Bad:

```text id="2x4v9m"
IRiskValidatorAndExecutionManager
```

An interface shall not combine
unrelated capabilities.

---

## Business-Oriented Naming

Interface names should describe
business responsibility.

Preferred:

```text id="p5q7t3"
ITradeLifecycleProvider

IOrderExecutor

IPortfolioProvider
```

Avoid:

```text id="w9f3s2"
IDataObject

IUtility

ICommonHelper
```

Interface names must represent
domain capability, not technical implementation.

---

## Forbidden Naming

The following names shall not be used:

* Helper.
* Utility.
* Common.
* Misc.
* Engine.
* Object.
* Thing.
* ManagerHelper.

These names do not communicate
business intent.

---

## Interface Ownership

Each interface shall have exactly one owner.

Example:

| Interface           | Owner Module      |
| ------------------- | ----------------- |
| IMarketProvider     | Market Module     |
| IBrainProvider      | Brain Module      |
| IAIDecisionProvider | AI Runtime Module |
| IRiskValidator      | Risk Module       |

Multiple ownership is prohibited.

The owner module is responsible for
maintaining the interface contract.

---

## Interface Stability

After publication, an interface name
shall remain stable.

Renaming requires:

* Architecture review.
* Impact analysis.
* Documentation update.
* Change approval.

Interface changes must follow
the project change management process.

---

## Review Checklist

Before creating a new interface:

| Check Item            | Required |
| --------------------- | -------- |
| Starts with I         | Yes      |
| Business-oriented     | Yes      |
| Single responsibility | Yes      |
| Approved suffix       | Yes      |
| Owner defined         | Yes      |

---

## Related Documents

* Coding_Standard.md
* MODULE_API_GUIDELINES.md
* MODULE_COMMUNICATION_STANDARD.md
* INTERFACE_CHANGE_POLICY.md
* CHANGE_REQUEST.md

---

## Document Status

Document:

`INTERFACE_NAMING_STANDARD.md`

Document Type:

Development Standard Document

Review Phase:

Phase 0.3 — Foundation Standards Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Document Status:

Approved Interface Naming Standard

---

End of INTERFACE_NAMING_STANDARD.md
