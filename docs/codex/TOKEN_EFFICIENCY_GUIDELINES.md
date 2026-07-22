# XAU AI PLATFORM TOKEN EFFICIENCY GUIDELINES

Version: 1.0.0

Status: Active

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines guidelines for efficient Codex usage within the XAU AI PLATFORM.

The purpose is to maximize implementation quality while reducing unnecessary context usage, repeated analysis, and inefficient development workflows.

---

## Scope

This guideline applies to all Codex-assisted activities, including:

- Code implementation.
- Code review.
- Documentation generation.
- Architecture analysis.
- Debugging sessions.

---

## Core Principles

Codex usage shall prioritize:

- Relevant context only.
- Clear task definition.
- Controlled scope.
- Complete deliverables.
- Minimal unnecessary repetition.

Efficiency must not reduce:

- Code quality.
- Architecture compliance.
- Documentation quality.
- Validation accuracy.

---

## 1. Context Management

Before starting work:

- Provide the required project context.
- Reference existing documentation.
- Identify affected modules.
- Define expected outputs.

Avoid providing:

- Unrelated files.
- Duplicate information.
- Outdated specifications.
- Unnecessary project history.

---

## 2. Task Definition

Each task should clearly define:

- Objective.
- Target files.
- Expected behavior.
- Constraints.
- Validation requirements.

Poor task definition increases:

- Repeated questions.
- Incorrect assumptions.
- Unnecessary iterations.

---

## 3. Documentation Usage

Codex should read documents in priority order:

1. Architecture documents.
2. Interface specifications.
3. Module specifications.
4. Coding standards.
5. Implementation files.

Only relevant documentation should be loaded for the current task.

---

## 4. File Delivery Standard

When modifying project files:

Required:

- Provide complete file content.
- Include full file path.
- Allow direct Copy → Replace workflow.
- Preserve existing standards.

Avoid:

- Partial snippets.
- Patch-only responses.
- Incomplete replacements.

---

## 5. Implementation Efficiency

Codex should:

- Understand existing code before modifying.
- Reuse existing components.
- Avoid unnecessary refactoring.
- Avoid duplicate implementations.
- Maintain module boundaries.

---

## 6. Review Efficiency

Before requesting review:

Perform:

- Self-review.
- Dependency check.
- Naming verification.
- Compile verification when applicable.

Provide review information clearly:

- Changed files.
- Purpose of changes.
- Validation status.

---

## 7. Session Continuity

For continued sessions:

Review:

- Previous session results.
- Remaining tasks.
- Current repository state.
- Active constraints.

Avoid restarting completed analysis unnecessarily.

---

## 8. Avoiding Token Waste

Avoid:

- Repeating unchanged requirements.
- Re-explaining approved architecture.
- Sending unnecessary files.
- Generating unused documentation.
- Creating duplicate solutions.

---

## 9. Quality Priority

Efficiency shall never override:

- Correctness.
- Maintainability.
- Security.
- Architecture compliance.
- Project standards.

The preferred approach is:

Quality first, efficient execution second.

---

## Completion Criteria

Token efficiency is achieved when:

- Required context is available.
- Tasks are clearly defined.
- Responses contain actionable outputs.
- No unnecessary repetition occurs.
- Project quality remains protected.

---

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-12 | Initial release. |
