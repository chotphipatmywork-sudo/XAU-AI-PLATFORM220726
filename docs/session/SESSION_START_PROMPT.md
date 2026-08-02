# Session Start Prompt

Version: 1.0.0

## Standard Bootstrap Prompt

You are resuming work on XAU-AI-PLATFORM220726. Read `docs/session/CURRENT_STATE.md` first. Work governance-first, evidence-first, specification-first, architecture-first, and within a narrow scope. Do not assume project status. Stop if evidence or authorization is insufficient.

## Mandatory Repository Verification

Verify the exact repository root, remote identity, current branch, HEAD, upstream, tracked working tree, staged state, and untracked inventory before any action.

## Mandatory CURRENT_STATE Verification

Compare the verified repository state with `CURRENT_STATE.md`. Report discrepancies before proceeding. Do not overwrite the state record merely to remove a discrepancy.

## Mandatory Git Verification

Use read-only Git inspection unless explicit Git authorization exists. Do not stage, commit, push, pull, fetch, merge, rebase, switch, or change configuration without authorization.

## Mandatory Authorization Verification

Identify the authorization ID, approved scope, allowed actions, forbidden actions, preconditions, expiration, and approval status. An implied request is not an authorization.

## Mandatory Scope Verification

List files and actions in scope. Confirm that the planned action does not alter architecture, implementation, runtime boundaries, governance, source data, or unrelated files.

## Start Decision

Proceed only when repository identity, state, authorization, and scope all pass. Otherwise stop and report the blocker.
