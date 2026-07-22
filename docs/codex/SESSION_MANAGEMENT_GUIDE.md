# XAU AI PLATFORM CODEX SESSION MANAGEMENT GUIDE

Version: 1.0.0

Status: Active

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the standard process for managing Codex development sessions within the XAU AI PLATFORM.

The purpose is to ensure every session starts with sufficient context, follows approved workflows, maintains project consistency, and produces traceable results.

---

## Scope

This guide applies to all Codex-assisted activities, including:

- Code implementation.
- Code review.
- Bug fixing.
- Refactoring.
- Documentation updates.
- Technical analysis.

---

## Session Lifecycle

Every Codex session shall follow these stages:

1. Session Preparation.
2. Session Startup.
3. Implementation Workflow.
4. Validation Process.
5. Session Closure.

---

## 1. Session Preparation

Before starting a session:

- Confirm the development objective.
- Identify required files and documents.
- Verify the current project state.
- Review applicable architecture constraints.
- Confirm implementation scope.

Required references should be available before making changes.

---

## 2. Session Startup

At the beginning of every session:

1. Open the repository root.
2. Start Codex from the root workspace.
3. Load the Session Start Prompt.
4. Review required project documentation.
5. Confirm current task scope.
6. Verify applicable project rules.

The session shall not begin implementation before required context is understood.

---

## 3. Context Management

Codex shall maintain sufficient context during implementation.

Required context includes:

- Current task objective.
- Related specifications.
- Module ownership.
- Dependency constraints.
- Existing implementation behavior.

Avoid:

- Unrelated modifications.
- Assumption-based changes.
- Scope expansion without approval.

---

## 4. Implementation Workflow

Every implementation task shall follow:

1. Read requirements.
2. Review related files.
3. Verify dependencies.
4. Implement approved changes.
5. Perform self-review.
6. Validate results.
7. Prepare final report.

---

## 5. Change Control

Changes shall follow project governance rules.

Codex shall:

- Modify only required files.
- Preserve existing architecture.
- Maintain compatibility.
- Avoid unnecessary refactoring.

Architecture-level changes require explicit approval.

---

## 6. Validation Process

Before completing a session, verify:

- Compile status.
- Test status when applicable.
- Dependency correctness.
- Documentation updates.
- Repository changes.

Any unresolved issue must be recorded.

---

## 7. Session Communication

Final session reporting shall include:

- Completed tasks.
- Modified files.
- Created files.
- Validation results.
- Known issues.
- Remaining work.
- Next steps.

---

## 8. Session Closure

A session is complete only when:

- Work is saved.
- Validation is completed.
- Documentation is updated when required.
- Final report is provided.

Use:

`SESSION_END_CHECKLIST.md`

before closing the session.

---

## 9. Session Continuation

When continuing previous work:

- Review the previous session result.
- Confirm remaining tasks.
- Verify current repository state.
- Continue from the approved stopping point.

Do not restart architectural decisions unless required.

---

## Completion Criteria

A Codex session is considered properly managed when:

- Session workflow is followed.
- Changes are traceable.
- Validation is completed.
- Project standards are maintained.

---

## Revision History

| Version | Date | Description |
| --- | --- | --- |
| 1.0.0 | 2026-07-12 | Initial release. |
