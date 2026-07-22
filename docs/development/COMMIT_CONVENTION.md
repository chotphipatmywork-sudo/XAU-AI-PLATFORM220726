# XAU AI PLATFORM — COMMIT CONVENTION

Version: 1.0.0

Status: Foundation Standard

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the commit message standard
for the XAU AI PLATFORM project.

The objective is to ensure that every change has:

* Clear identification.
* Traceable history.
* Consistent description.
* Review-friendly information.

Commit messages are part of
the project development record.

---

## Commit Principles

Every commit shall:

* Represent one logical change.
* Describe the purpose clearly.
* Follow the naming convention.
* Avoid unrelated modifications.
* Support future investigation.

A commit should explain
why a change exists.

---

## Commit Message Format

All commits shall follow:

```text
<Type>: <Description>
```

Examples:

```text
feat: add trend analyzer

fix: correct risk calculation

docs: update architecture guide
```

---

## Commit Type Standard

Approved commit types:

| Type     | Purpose                                  |
| -------- | ---------------------------------------- |
| feat     | New functionality                        |
| fix      | Bug correction                           |
| docs     | Documentation change                     |
| refactor | Code improvement without behavior change |
| test     | Test related change                      |
| build    | Build system change                      |
| chore    | Maintenance task                         |
| perf     | Performance improvement                  |

---

## Feature Commit

Use:

```text
feat: <feature description>
```

Examples:

```text
feat: add volatility engine

feat: implement risk validator
```

Feature commits should represent
completed development units.

---

## Bug Fix Commit

Use:

```text
fix: <problem description>
```

Examples:

```text
fix: resolve execution validation error

fix: correct position state update
```

Bug fix commits should identify
the corrected behavior.

---

## Documentation Commit

Use:

```text
docs: <documentation description>
```

Examples:

```text
docs: update package blueprint

docs: add module lifecycle standard
```

Documentation changes must remain
traceable.

---

## Commit Scope Rules

Each commit should focus
on one area.

Recommended:

```text
feat: add trend package

fix: correct order validation

docs: update api guideline
```

Avoid:

```text
feat: add trend package and fix risk and update docs
```

A commit containing unrelated changes
reduces traceability.

---

## Commit Description Rules

Commit descriptions should:

* Be clear and concise.
* Describe the actual change.
* Use present tense.
* Avoid unnecessary details.

Preferred:

```text
feat: add liquidity analyzer
```

Avoid:

```text
added some changes
```

---

## Breaking Change Convention

Changes that affect architecture
contracts must be identified.

Examples:

```text
feat!: change execution interface

refactor!: update package contract
```

Breaking changes require:

* Architecture review.
* Impact analysis.
* Documentation update.
* Approval before merge.

---

## Commit Validation Rules

Before committing:

* Code must compile.
* Tests must pass when available.
* Documentation must be updated when required.
* No temporary files included.

Invalid commits should not enter
shared branches.

---

## Commit History Rules

Commit history should provide:

* Clear development timeline.
* Change ownership.
* Reason for modification.
* Recovery reference.

Commit messages become part of
project knowledge.

---

## Review Checklist

Before accepting a commit:

| Check Item           | Required |
| -------------------- | -------- |
| Correct format       | Yes      |
| Type selected        | Yes      |
| Description clear    | Yes      |
| Single purpose       | Yes      |
| Validation completed | Yes      |

---

## Related Documents

* BRANCHING_STRATEGY.md
* REVIEW_PROCESS.md
* CHANGE_REQUEST.md
* VERSIONING_POLICY.md
* DOCUMENTATION_GOVERNANCE.md

---

## Document Status

Document:

`COMMIT_CONVENTION.md`

Document Type:

Development Standard Document

Review Phase:

Phase 0.3 — Foundation Development Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Document Status:

Approved Commit Convention

---

End of COMMIT_CONVENTION.md
