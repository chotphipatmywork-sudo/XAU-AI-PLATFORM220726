# XAU AI PLATFORM — DIRECTORY OWNERSHIP

Version: 1.0.0

Status: Foundation Standard

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines directory ownership rules
for the XAU AI PLATFORM project.

The objective is to ensure that every directory has:

* Clear responsibility.
* Defined ownership.
* Controlled modification.
* Predictable structure.

Directory ownership protects
architecture boundaries.

---

## Ownership Principles

Every directory shall:

* Have one responsible owner.
* Contain only related responsibilities.
* Follow approved structure.
* Avoid unrelated files.
* Preserve dependency boundaries.

A directory represents an architectural
responsibility area.

---

## Ownership Model

The project uses:

```text id="3kq9mv"
Directory

    |

    v

Module Owner

    |

    v

Responsible Maintainer
```

The owner controls changes
inside the assigned directory.

---

## Root Directory Ownership

The project root contains:

| Directory | Responsibility             |
| --------- | -------------------------- |
| core      | Main system implementation |
| docs      | Project documentation      |
| tests     | Testing resources          |
| tools     | Development utilities      |

Each root directory has
independent responsibility.

---

## Core Directory Ownership

The `core` directory contains
system modules.

Structure:

```text id="q7c0rm"
core/

├── market/
├── brain/
├── ai/
├── risk/
├── execution/
├── trade/
├── position/
└── portfolio/
```

Each module directory owns
its internal implementation.

---

## Module Directory Ownership

A module directory shall contain only:

* Module implementation.
* Module models.
* Module configuration.
* Module services.
* Module documentation.

Example:

```text id="s0kq61"
risk/

├── config/
├── models/
├── engines/
├── services/
└── analyzer/
```

---

## Ownership Boundaries

Directory owners are responsible for:

* Maintaining structure.
* Reviewing changes.
* Protecting dependencies.
* Updating documentation.

External modules shall not modify
internal files without approval.

---

## Documentation Directory Ownership

The `docs` directory contains
project knowledge and governance documents.

Structure:

```text id="8p5t7x"
docs/

├── architecture/
├── standards/
├── development/
├── project/
├── specifications/
└── templates/
```

Each documentation area has
a defined purpose.

---

## File Placement Rules

Files shall be placed according
to responsibility.

Examples:

| File Type              | Location          |
| ---------------------- | ----------------- |
| Architecture decisions | docs/architecture |
| Development rules      | docs/development  |
| Coding standards       | docs/standards    |
| Project management     | docs/project      |
| Templates              | docs/templates    |

Files shall not be placed
in unrelated directories.

---

## Directory Modification Rules

Changes to directories require:

* Understanding ownership.
* Reviewing dependencies.
* Following naming rules.
* Updating documentation when required.

Unauthorized structural changes
are prohibited.

---

## Duplicate Structure Prevention

The project shall avoid:

* Duplicate directories.
* Duplicate ownership.
* Multiple locations for the same responsibility.

A responsibility must have
one primary location.

---

## Ownership Transfer

If ownership changes:

* New owner must be defined.
* Documentation must be updated.
* Existing dependencies must be reviewed.

Ownership changes require
controlled approval.

---

## Review Checklist

Before adding or changing directories:

| Check Item            | Required |
| --------------------- | -------- |
| Ownership defined     | Yes      |
| Responsibility clear  | Yes      |
| Structure approved    | Yes      |
| Dependencies reviewed | Yes      |
| Documentation updated | Yes      |

---

## Related Documents

* PROJECT_STRUCTURE.md
* MODULE_DEPENDENCY_RULES.md
* CHANGE_REQUEST.md
* DOCUMENTATION_GOVERNANCE.md
* ARCHITECTURE_FREEZE.md

---

## Document Status

Document:

`DIRECTORY_OWNERSHIP.md`

Document Type:

Development Standard Document

Review Phase:

Phase 0.3 — Foundation Development Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Document Status:

Approved Directory Ownership Standard

---

End of DIRECTORY_OWNERSHIP.md
