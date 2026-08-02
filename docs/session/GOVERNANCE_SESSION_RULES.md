# Governance Session Rules

Version: 1.0.0

Architecture Baseline: ABR-1.0

## Session Lifecycle

1. Bootstrap by reading `CURRENT_STATE.md`.
2. Verify repository identity and Git state.
3. Verify authorization and scope.
4. Collect evidence.
5. Perform only authorized work.
6. Validate results and repository integrity.
7. Record handoff and close-out status.

## Governance Checkpoints

Checkpoints are required before action, after material work, before any state transition, and before session close-out.

## Scope Control

The approved work item defines the maximum scope. New files, architecture changes, implementation, execution, and Git actions require explicit authorization.

## Evidence Requirements

Evidence SHALL identify its source, date or observation context where available, applicability, limitations, and relationship to the work item. Missing evidence SHALL remain missing.

## Authorization Requirements

Authorization SHALL identify scope, allowed actions, forbidden actions, preconditions, expiration, approval status, and authority. Approval for one phase SHALL NOT be reused for another phase.

## Escalation Rules

Stop and escalate when repository identity is ambiguous, required evidence conflicts or is absent, scope expands, a blocker cannot be resolved within scope, or an action would modify Git, architecture, implementation, or governance.

## State Integrity

No session may silently change `CURRENT_STATE.md`, governance decisions, blocker status, or deferred limitations to make work appear complete.
