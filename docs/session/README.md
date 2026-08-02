# AI Session State Framework

Version: 1.0.0

Status: Active

Document Type: Session governance guide

Architecture Baseline: ABR-1.0

## Purpose

This folder provides the controlled handoff and continuity records required for future ChatGPT and Codex sessions.

## Folder Contents

- `CURRENT_STATE.md` — current verified project state.
- `SESSION_START_PROMPT.md` — bootstrap instructions for a new session.
- `SESSION_END_CHECKLIST.md` — close-out checklist.
- `GOVERNANCE_SESSION_RULES.md` — session governance rules.
- `SESSION_STATE_TEMPLATE.md` — reusable state template.
- `AUTHORIZATION_TEMPLATE.md` — reusable authorization record.
- `HANDOFF_TEMPLATE.md` — reusable session handoff record.
- `DECISION_LOG.md` — governance decision register.

## Update Workflow

1. Read `CURRENT_STATE.md` before work.
2. Verify repository, branch, HEAD, and working tree.
3. Confirm explicit authorization and scope.
4. Record evidence before changing state.
5. Update only the authorized state or handoff records.
6. Re-verify the repository and record the next action.

## Governance Workflow

Every session SHALL preserve the active governance state, distinguish evidence from assumptions, and stop when required evidence or authorization is missing.

## Relationship with Git

These documents describe project state; Git remains the authoritative source for committed repository history. Uncommitted changes, untracked files, branches, and remote state SHALL be reported separately.

## Single Source of Truth

`CURRENT_STATE.md` is the single source of truth for the latest verified session state. Other documents define procedures, templates, or historical decisions and SHALL NOT silently override it.
