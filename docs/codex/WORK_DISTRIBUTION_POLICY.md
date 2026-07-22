# XAU AI PLATFORM CODEX WORK DISTRIBUTION POLICY

Version: 1.0.0

Status: Active

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the work distribution policy for Codex-assisted development within the XAU AI PLATFORM.

The purpose is to establish clear responsibility boundaries, prevent unauthorized decisions, and ensure development activities follow the approved project governance model.

---

## Scope

This policy applies to all Codex-assisted activities, including:

- Feature implementation.
- Bug fixing.
- Refactoring.
- Documentation updates.
- Technical reviews.
- Development analysis.

---

## Core Principle

Codex is an implementation assistant.

Codex may execute approved work but shall not independently redefine:

- Project architecture.
- Business requirements.
- Module ownership.
- System boundaries.
- Development strategy.

---

## 1. Responsibility Roles

### Project Owner

Responsible for:

- Final project decisions.
- Architecture approval.
- Scope approval.
- Priority decisions.
- Major change authorization.

---

### Architecture Owner

Responsible for:

- Architecture consistency.
- Module boundaries.
- Interface decisions.
- Dependency rules.
- Architecture evolution.

---

### Developer

Responsible for:

- Implementation execution.
- Code quality.
- Local validation.
- Technical investigation.
- Reporting implementation results.

---

### Codex

Responsible for:

- Assisting implementation.
- Following approved specifications.
- Generating complete implementations.
- Supporting review activities.
- Maintaining project standards.

---

## 2. Codex Allowed Activities

Codex may:

- Implement approved features.
- Modify assigned files.
- Create new files within approved scope.
- Improve internal implementation quality.
- Generate documentation requested by the project.
- Perform code analysis and review.

---

## 3. Codex Restricted Activities

Codex shall not:

- Change architecture independently.
- Redesign modules without approval.
- Create alternative solutions outside scope.
- Rename public interfaces without approval.
- Move ownership between modules.
- Add dependencies without justification.
- Remove existing functionality without instruction.

---

## 4. Task Assignment Rules

Every task should define:

- Objective.
- Scope.
- Target files.
- Expected output.
- Validation requirements.

If the scope is unclear:

- Stop implementation.
- Request clarification.
- Do not make assumptions.

---

## 5. File Ownership Rules

Changes must follow:

- Existing folder ownership.
- Module responsibility boundaries.
- Dependency direction rules.

Codex shall avoid modifying files outside the assigned scope unless required for a valid dependency update.

---

## 6. Change Escalation

Escalation is required when:

- Architecture changes are needed.
- Public interfaces must change.
- Requirements conflict.
- Existing standards are insufficient.
- Module responsibilities are unclear.

Implementation shall not continue until approval is provided.

---

## 7. Review Responsibility

Before completion:

Codex shall provide:

- Modified files.
- Created files.
- Change summary.
- Validation results.
- Known issues.
- Remaining work.

The final decision remains with the project review process.

---

## 8. Work Priority

Development priority shall follow:

1. Architecture compliance.
2. Correct implementation.
3. Validation quality.
4. Documentation completeness.
5. Efficiency improvement.

Speed shall not override project stability.

---

## Completion Criteria

Work distribution is considered successful when:

- Responsibilities are clearly defined.
- Scope boundaries are respected.
- Changes are traceable.
- Review requirements are satisfied.
- Architecture integrity is maintained.

---

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-12 | Initial release. |
