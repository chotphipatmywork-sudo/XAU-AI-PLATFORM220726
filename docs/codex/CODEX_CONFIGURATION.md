# XAU AI PLATFORM CODEX CONFIGURATION

Version: 1.0.0

Status: Active

Architecture Baseline: ABR-1.0

---

## Purpose

This document defines the recommended Codex CLI configuration for the XAU AI PLATFORM.

The purpose is to standardize the Codex execution environment and ensure consistent behavior across development machines, sessions, and implementation workflows.

---

## Scope

This document applies to all developers and contributors using Codex CLI for the XAU AI PLATFORM project.

The configuration rules defined here support:

- Consistent development environments.
- Controlled AI-assisted development workflows.
- Stable repository operations.
- Reliable implementation sessions.

---

## References

- `docs/codex/CODEX_CONTRACT.md`
- `docs/project/PROJECT_INDEX.md`
- `docs/project/ARCHITECTURE_FREEZE.md`
- `docs/project/DEFINITION_OF_DONE.md`

---

## 1. Supported Versions

### Minimum Version

```text
0.144.1
Recommended Version

Use the latest stable release officially supported by OpenAI.

Update Policy

Codex should be updated before starting a new development phase.

Version changes should be reviewed when they may affect:

Execution behavior.
Tool availability.
Repository workflows.
Development standards.
2. Recommended Model

The project default model shall follow the organization-approved configuration.

Models should only be changed when explicitly required by:

Project requirements.
Performance evaluation.
Development constraints.
3. Working Directory

Codex must always be launched from the repository root directory.

Required:

Open the XAU AI PLATFORM repository root.
Start Codex from the root workspace.

Avoid:

Starting sessions from module subdirectories.
Working outside the repository context.
4. Sandbox Policy

Recommended default:

Workspace Write

Usage policy:

Mode    Usage
Read Only   Documentation review and analysis tasks
Workspace Write Standard implementation workflow
Danger Full Access  Requires explicit approval

Danger Full Access should never be enabled without project owner approval.

5. Approval Policy

Recommended approval mode:

on-request

Approval rules:

Review actions before execution.
Confirm destructive operations.
Maintain controlled repository changes.

Approval restrictions must not be disabled without project owner approval.

6. Repository Policy

The repository shall:

Maintain a clean working tree before implementation.
Follow the defined branch strategy.
Follow commit conventions.
Preserve project architecture boundaries.
Avoid unauthorized structural changes.

All changes must comply with project governance documents.

7. Session Startup

Before starting implementation work:

Open the repository root.
Start Codex.
Load the Session Start Prompt.
Read required project documentation.
Confirm the current development context.
Verify applicable rules and constraints.

Required references should be reviewed before making changes.

8. Session Shutdown

Before ending a development session:

Save all completed work.
Perform self-review.
Verify documentation updates.
Confirm validation status.
Record remaining tasks.
Prepare the next session state.
9. Diagnostics

Recommended diagnostic command:

codex doctor

Run diagnostics:

After installation.
After major configuration changes.
When unexpected behavior occurs.
10. Future Configuration

This document may be extended to define additional Codex configuration standards:

Profiles.
MCP integration.
Plugins.
Remote execution.
Shared team configuration.
Automated workflow settings.

Any future extension must maintain compatibility with the XAU AI PLATFORM architecture governance.

Revision History
VersionDate Description
1.0.0   2026-07-12  Initial release.
