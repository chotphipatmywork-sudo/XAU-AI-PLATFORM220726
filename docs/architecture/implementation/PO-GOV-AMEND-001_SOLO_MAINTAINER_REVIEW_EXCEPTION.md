# PO-GOV-AMEND-001 Solo-Maintainer Review Exception

Version: 1.0.0
Status: Proposed — Not Effective
Document Type: Governance Amendment
Amendment ID: PO-GOV-AMEND-001
Governance Owner: Project Owner
Architecture Baseline: ABR-1.0
Effective Date UTC: Pending approval, merge, and verification

## Purpose

Define a narrow, auditable waiver of independent approval when no eligible
independent reviewer exists. The waiver is not independent approval and does
not convert self-review into independent review.

## Authority and Governance Relationship

This amendment is subordinate to the Architecture Baseline, effective
governance decisions, branch controls, and mandatory validation gates. It does
not weaken direct-main protections or authorize any merge while Proposed or
unverified.

## Scope

Permitted candidate categories are limited to non-executable:

- Governance documents.
- Architecture documents.
- Research evidence reports.
- Closure reports.
- Documentation indexes.
- Metadata-only documentation records.

Eligibility requires full scope review; document category alone is insufficient.

## Definitions

- Independent reviewer: an eligible account other than the pull-request author.
- Solo-maintainer condition: the deterministic condition in this amendment.
- Exception authorization: one Project Owner authorization bound to one exact PR.
- Effective amendment: this document after approval, authorized merge, and
  successful post-merge verification.

## Eligibility Conditions

All conditions SHALL be satisfied:

- Exactly one active repository collaborator or maintainer with relevant
  review or merge authority exists.
- That sole active authorized account is the pull-request author.
- No other active account qualifies as an independent reviewer.
- No pending invitation could provide an eligible independent reviewer.
- Organization membership, team access, outside collaborators, repository
  collaborators, and other relevant permission sources are checked where
  applicable.
- Reviewer eligibility is determined from current governance and permissions,
  not collaborator-list length alone.
- The condition is freshly verified.
- The pull request uses an approved dedicated branch and is current and clean.
- All applicable gates pass.
- A pull-request-specific Project Owner authorization is recorded.

## Reviewer Availability Verification

Invitation evidence may be treated as empty only when the request succeeds,
the authenticated identity and repository are verified, the response is valid
JSON, its top-level value is an array, the array is semantically empty, and
pagination or permission limits cannot hide results.

Null, incomplete, ambiguous, denied, truncated, or structurally unexpected
responses SHALL be treated as unresolved, not as zero invitations or reviewers.
PowerShell collection counting SHALL NOT be the sole evidence.

## Pull Request Identity Binding

The following SHALL match the values recorded in the exact Project Owner
authorization:

- Pull-request number.
- Base branch.
- Head branch.
- Head SHA.
- Commit count.
- File count.
- Authorized file inventory.
- Required merge method.
- Protected pull-request isolation requirements.

Any mismatch invalidates the authorization and requires a mandatory stop.

## Required Substitute Controls

The evidence package SHALL separately record:

- Fresh PR identity and branch verification.
- Remote base SHA and ahead/behind relationship.
- Exact commit and file inventories.
- Full file-scope and document-quality review.
- Applicable PR-G1 through PR-G8 results.
- Scorecard, delta, and root-cause records.
- Exact authorization ID and merge method.
- Protected-PR isolation.
- Merge result, two-parent validation, remote-main reachability, and
  post-merge verification.
- Evidence, Governance Record, Authorization, Blocker, Deferred Scope, Gate,
  Scorecard, Delta, Root Cause, Git working tree, Merge result, and
  Post-merge verification as distinct record classes.

## Project Owner Authorization Model

Authorization SHALL be:

- Per pull request.
- Bound to one exact head SHA and file inventory.
- Bound to one required merge method.
- Non-transferable and non-reusable.
- Invalidated by any material PR, collaborator, invitation, permission,
  governance, blocker, gate, or scope change.
- Revoked by the Project Owner or superseded through the explicit rule below.
- Expired when an eligible reviewer becomes available.

It SHALL NOT create standing merge authority or be inferred from an earlier
authorization.

## Mandatory Stop Conditions

Stop without merge authorization for any change in:

- PR identity, branch, head SHA, commit count, or file count.
- Base branch, remote base SHA, or ahead/behind relationship.
- Reviewer, collaborator, team, invitation, or permission state.
- Gate, scorecard, check, mergeability, or conflict state.
- Evidence, authorization, protected-PR state, or working-tree explanation.

Staged changes, tracked modifications, unexplained in-scope untracked files,
missing evidence, or ambiguous API responses are blocking states.

## Working Tree Classification

### Blocking State

The following block the operation:

- Unstaged or staged changes not explicitly authorized.
- Tracked modifications not explicitly authorized.
- Unexplained in-scope untracked files.
- Unexplained repository-state changes.
- Dependence on uncommitted local content.

### Non-Blocking but Recordable State

Pre-existing unrelated untracked files may remain only when they existed before
the operation, are outside scope, are not staged or changed, and are recorded
under Evidence and Deferred Scope. They SHALL NOT be deleted, cleaned, stashed,
moved, committed, or included.

## Prohibited Uses

This amendment SHALL NOT:

- Treat self-approval as independent review.
- Waive technical gates, evidence requirements, failures, or conflicts.
- Permit admin bypass, auto-merge, squash, rebase, force push, or branch deletion.
- Permit executable, runtime, trading, Brain, AI, Risk, Execution, script,
  build, deployment, test-execution, credential, secret, security, binary,
  dataset, backup-restoration, or destructive changes.
- Apply automatically to future pull requests.
- Expand by similarity or retroactively validate an unauthorized merge.
- Authorize rollback.
- Approve, waive, modify, or merge PR #1.

## Evidence and Audit Records

Separate records SHALL preserve Evidence, Governance Record, Authorization,
Blocker, Deferred Scope, Gate, Scorecard, Delta, Root Cause, Git working tree,
Merge result, and Post-merge verification.

## Expiry and Revocation

The exception expires when another eligible reviewer becomes available. It SHALL
be reassessed after collaborator, permission, governance, or PR changes and may
be revoked by the Project Owner. It does not survive material changes to the
authorized PR.

## Applicability to PR #1

This amendment does not approve PR #1, waive any PR #1 gate, or issue PR #1
merge authorization. It cannot apply while Proposed or unverified. PR #1 SHALL
undergo a fresh separate reassessment after this amendment is effective, with
a new authorization bound to the exact then-current PR #1 identity and head
SHA. The currently recorded PR #1 SHA is historical evidence only.

No action on PR #1 is authorized during this revision.

## Effective-State Rule

This amendment remains not effective until all of the following are verified:

1. Project Owner approval of the exact amendment content.
2. Authorized creation of the governance file.
3. Controlled governance branch and pull request.
4. Required pre-merge gates.
5. Exact Project Owner merge authorization.
6. Merge using the authorized merge method.
7. Successful mandatory post-merge verification.
8. Confirmation that the exact approved document blob is reachable from
   `origin/main`.

A draft, branch, commit, open or approved PR, attempted merge, or closed PR does
not make this amendment effective.

## Supersession Rule

A later governance document supersedes this amendment only when it explicitly:

- Identifies `PO-GOV-AMEND-001`.
- States that it supersedes or replaces this amendment.
- Is approved through an authorized governance workflow.
- Is merged through that workflow.
- Passes mandatory post-merge verification.
- Is confirmed effective in `origin/main`.

A merely newer or related document does not supersede this amendment.

## Blocker Handling

Any unresolved evidence, authority, reviewer, invitation, scope, gate,
working-tree, or API ambiguity remains a blocker. No ambiguity may be resolved
in favor of expanded authority.

## Deferred Scope

The following remain deferred until separate authorization:

- Project Owner approval.
- File creation, branch, commit, push, PR creation, review, and merge.
- Amendment effectiveness verification.
- Application of the exception.
- PR #1 reassessment, review, approval, modification, or merge.
- BLK-006 closure.
- Branch cleanup or local synchronization.
- Runtime, research implementation, source-code, dataset, and artifact work.
