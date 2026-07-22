# XAU AI PLATFORM CODEX RULES

Version: 1.0.0

Status: Active

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the permanent rules that Codex must follow when contributing to the XAU AI PLATFORM.

These rules are mandatory and apply to all Codex-assisted development activities.

---

## General Rules

Codex shall:

- Follow `Coding_Standard.md`.
- Follow `ProjectStructure.md`.
- Follow `NamingConvention.md`.
- Preserve the approved architecture.
- Avoid redesigning existing modules without approval.
- Never rename folders without approval.
- Never rename public classes without approval.
- Never delete existing code without instruction.
- Maintain backward compatibility.

---

## File Rules

All files shall follow these rules:

- One Class Per File.
- One Responsibility Per Class.
- Include Guard is required.
- Header Comment is required.
- Consistent naming is required.
- Duplicate files are prohibited.

---

## Coding Rules

Codex shall ensure:

- No global variables.
- No magic numbers.
- No hardcoded paths.
- No TODO items unless explicitly requested.
- No placeholder implementations.
- No dead code.
- Small and readable functions.
- Prefer composition over inheritance.
- Follow SOLID principles.

---

## Architecture Rules

Codex must preserve the approved project architecture.

The following actions are forbidden:

- Creating alternative architectures.
- Moving modules without approval.
- Changing folder hierarchy.
- Introducing unnecessary dependencies.
- Breaking existing interfaces.

Architecture changes require explicit approval before implementation.

---

## Dependency Rules

Before adding any include, Codex shall verify:

- The target file already exists.
- Dependency direction is valid.
- Circular dependencies are avoided.
- Unused includes are removed.

---

## Modification Rules

Codex shall only modify files explicitly assigned or required by the approved implementation scope.

Codex shall not modify unrelated files.

---

## Documentation Rules

Every new module shall include:

- Header comment.
- Purpose description.
- Version information.
- Author information when required by project standards.
- Update history when applicable.

Documentation changes must follow project documentation standards.

---

## Validation Before Completion

Before completing a task, Codex shall verify:

- No compile errors.
- No missing includes.
- No duplicate classes.
- No duplicate files.
- No syntax errors.
- Consistent naming.
- Compliance with applicable standards.

---

## Output Format

The final response shall include:

1. Files Modified.
2. Summary of Changes.
3. Compile Status.
4. Warnings.
5. Remaining Work.

---

## Completion Criteria

A task is complete only when:

- Approved scope is implemented.
- Required validation is completed.
- Documentation requirements are satisfied.
- No blocking issues remain.

---

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-12 | Initial release. |
