# XAU AI PLATFORM - DEVELOPMENT GUIDE INDEX

Version: 1.0.0

Status: Foundation Standard

Architecture Baseline: ABR-1.0

---

## Purpose

This document provides an index and overview of development governance documents within the XAU AI PLATFORM project.

The objective is to define the role of the `docs/development` directory and guide developers and AI Coding Assistants through development standards.

---

## Development Governance Purpose

The `development` documentation area defines rules for:

* Development workflow
* Configuration management
* Dependency control
* Error handling
* Logging
* Security
* Testing

These documents ensure consistent implementation practices.

---

## Development Documentation Structure

The folder contains:

```text id="w9f5l2"
development/

├── BRANCHING_STRATEGY.md
├── COMMIT_CONVENTION.md
├── CONFIGURATION_GUIDE.md
├── DIRECTORY_OWNERSHIP.md
├── ERROR_HANDLING_GUIDE.md
├── LOGGING_GUIDE.md
├── MODULE_DEPENDENCY_RULES.md
├── SECURITY_GUIDELINES.md
└── TESTING_GUIDE.md
```

Each document has a specific responsibility.

---

## Document Categories

### Workflow Management

Documents:

* BRANCHING_STRATEGY.md
* COMMIT_CONVENTION.md

Purpose:

Define source control and collaboration rules.

---

### Configuration Management

Document:

* CONFIGURATION_GUIDE.md

Purpose:

Define configuration ownership, validation, and lifecycle.

---

### Structure Governance

Document:

* DIRECTORY_OWNERSHIP.md

Purpose:

Define directory responsibilities and ownership boundaries.

---

### Reliability Management

Documents:

* ERROR_HANDLING_GUIDE.md
* LOGGING_GUIDE.md

Purpose:

Define failure management and observability standards.

---

### Architecture Protection

Document:

* MODULE_DEPENDENCY_RULES.md

Purpose:

Control module communication and dependency direction.

---

## Security and Quality Management

Documents:

* SECURITY_GUIDELINES.md
* TESTING_GUIDE.md

Purpose:

Define security practices and validation requirements before integration.

---

## Recommended Reading Order

Developers should read documents in the following order:

```text id="u7zq8m"
1. DIRECTORY_OWNERSHIP.md

↓

2. MODULE_DEPENDENCY_RULES.md

↓

3. CONFIGURATION_GUIDE.md

↓

4. ERROR_HANDLING_GUIDE.md

↓

5. LOGGING_GUIDE.md

↓

6. SECURITY_GUIDELINES.md

↓

7. TESTING_GUIDE.md

↓

8. BRANCHING_STRATEGY.md

↓

9. COMMIT_CONVENTION.md
```

This order provides understanding from structure to implementation control.

---

## Development Rules Summary

All development activities shall follow:

* Architecture before implementation
* Explicit ownership
* Controlled dependencies
* Documented changes
* Validation before integration

Development rules are mandatory project standards.

---

## Relationship With Other Documentation

The development documentation works together with:

| Documentation Area | Responsibility               |
| ------------------ | ---------------------------- |
| architecture       | System design rules          |
| standards          | Technical standards          |
| project            | Project governance           |
| codex              | AI Coding Assistant workflow |
| specifications     | Technical specifications     |

---

## Development Review Process

Development changes follow:

```text id="4m8s0q"
Implementation

↓

Testing

↓

Review

↓

Documentation Update

↓

Integration
```

No incomplete implementation should be integrated.

---

## Review Checklist

Before completing development documentation:

| Check Item                   | Required |
| ---------------------------- | -------- |
| Documents indexed            | Yes      |
| Responsibilities defined     | Yes      |
| Reading order provided       | Yes      |
| Related documents referenced | Yes      |
| Markdownlint passed          | Yes      |

---

## Document Status

Version:

1.0.0

Status:

Foundation Standard

Architecture Baseline:

ABR-1.0

Document Status:

Approved Development Guide Index

---

## End of DEVELOPMENT GUIDE INDEX
