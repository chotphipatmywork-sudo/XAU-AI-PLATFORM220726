# PO-GOV-AUTH-001 Foundational Governance Authority Decision

Version: 1.0.0
Status: Approved — Prospective Foundational Authority
Decision ID: PO-GOV-AUTH-001
Decision Date UTC: 2026-07-30
Document Type: Foundational Governance Authority Decision
Architecture Baseline: ABR-1.0

## Purpose

Establish the minimum prospective Project Owner authority required to resolve
a verified solo-maintainer governance deadlock through a controlled,
auditable governance-bootstrap procedure.

This decision does not make the proposed Solo-Maintainer Review Exception
effective and does not authorize merging BLK-006 Pull Request #1.

## Background

The repository operates under a verified solo-maintainer condition:

- Owner and sole direct collaborator: `chotphipatmywork-sudo`.
- No eligible non-author collaborator exists.
- No pending collaborator invitation exists.
- Team-based access is not applicable to this personal-account repository.
- No independent approval has been submitted for BLK-006 Pull Request #1.

Existing governance requires review and approval before merge but does not
define an approved mechanism for waiving independent approval or resolving
the resulting deadlock.

## Decision

The Project Owner approves and establishes prospective authority to define and
execute a controlled governance-bootstrap procedure. This is not independent
review and must not be represented as independent approval.

GitHub administrative capability alone is not treated as governance authority;
this authority is established by this explicit, auditable decision.

## Authorized Bootstrap Scope

This decision authorizes only the following controlled sequence:

1. Record this decision on a dedicated governance branch.
2. Create a pull request containing only this decision record.
3. Perform read-only governance, branch, commit, file-scope, document, and
   mergeability gates.
4. Record the solo-maintainer condition and absence of an eligible independent
   reviewer.
5. Issue a separate pull-request-specific Bootstrap Merge Authorization after
   all required gates pass.
6. Merge the foundational decision using merge commit only.
7. Perform and record mandatory post-merge verification.
8. Propose a separate Solo-Maintainer Review Exception amendment.

Each stage requires its own evidence and authorization.

## Initial Repository-Recording Authorization

The immediate authorization is limited to:

- Creating branch `governance/po-gov-auth-001` from `origin/main`.
- Creating this canonical file.
- Validating the branch, document, and one-file scope.
- Creating one controlled commit:
  `docs(governance): record PO-GOV-AUTH-001`.
- Pushing only the dedicated governance branch.

Pull request creation, approval, and merge are not authorized by this task.

## Prospective Effect

This decision becomes effective as repository governance for subsequent
amendments only after it is merged into `main` using merge commit and the
post-merge verification passes. An unmerged branch record is not a general
governance amendment.

## Required Pull Request and Branch Controls

All later work under this decision must:

- Use a dedicated branch and a pull request targeting `main`.
- Preserve the prohibition on direct commits to `main`.
- Remain current, conflict-free, and mergeable.
- Pass all applicable manual gates.
- Preserve commit and file-scope evidence.
- Use merge commit only when separately authorized.
- Receive mandatory post-merge verification.

## Bootstrap Merge Authorization

This decision does not authorize its own merge. A separate Project Owner
Bootstrap Merge Authorization is mandatory after pull request identity,
commit integrity, file scope, document quality, governance scope, branch
compliance, base currency, and reviewability gates pass.

## Prohibited Uses

This decision must not be used to:

- Claim author review is independent review.
- Bypass failed gates, conflicts, or unauthorized scope.
- Commit directly to `main`, force push, rewrite history, squash merge, or
  rebase merge.
- Combine unrelated files or modify runtime, trading, Brain, AI, Risk,
  Execution, Portfolio, Learning, source data, backup artifacts, credentials,
  security controls, build, or deployment configuration.
- Apply a waiver automatically to any future pull request.
- Treat the Solo-Maintainer Review Exception as effective.
- Merge BLK-006 Pull Request #1.

## Solo-Maintainer Review Exception Boundary

The Solo-Maintainer Review Exception remains a separate proposed amendment.
It must define eligibility, waiver semantics, documentation-only scope, all
pull-request gates, base currency, mergeability, pull-request-specific Project
Owner authorization, prohibited technical/security scope, merge strategy,
post-merge verification, effective-date rules, and fresh authorization for
each qualifying pull request.

No provision of that exception is effective merely because this decision was
approved or recorded.

## BLK-006 Pull Request Boundary

BLK-006 Pull Request #1 remains outside this decision's authorization scope:

- Pull Request: `#1`
- State: `OPEN`
- Independent Approval: `NOT RECORDED`
- Solo-Maintainer Review Exception: `NOT EFFECTIVE`
- Merge Authorization: `NOT GRANTED`

It may be reassessed only after this decision is merged and verified, the
separate exception becomes effective, reviewer availability is freshly
verified, PR-G1 through PR-G8 are freshly verified, and a PR-specific
Solo-Maintainer Merge Authorization is issued.

## Required Audit Records

The controlled workflow must preserve this decision, branch and commit
evidence, pull-request identity and scope, manual gate results, solo-maintainer
verification, Bootstrap Merge Authorization, merge evidence, post-merge
verification, exception-amendment evidence, and PR-specific authorization and
post-merge verification.

## Architecture and Governance Preservation

The following controls remain in force:

| Control | Status |
| --- | --- |
| Direct commits to `main` | PROHIBITED |
| Dedicated branch | REQUIRED |
| Pull request | REQUIRED |
| Applicable review gates | REQUIRED |
| Failing checks | CANNOT BE WAIVED |
| Merge conflicts | CANNOT BE WAIVED |
| Merge strategy | MERGE COMMIT ONLY |
| Force push | PROHIBITED |
| Squash merge | PROHIBITED |
| Rebase merge | PROHIBITED |
| Project Owner merge authorization | REQUIRED |
| Post-merge verification | REQUIRED |

## Decision Status

- Project Owner Decision: APPROVED
- Foundational Governance Authority: ESTABLISHED PROSPECTIVELY
- Solo-Maintainer Condition: CONFIRMED
- Controlled Bootstrap: AUTHORIZED SUBJECT TO STAGED AUTHORIZATION
- Initial Repository Recording: AUTHORIZED
- General Governance Amendment: NOT YET EFFECTIVE
- Solo-Maintainer Review Exception: NOT YET EFFECTIVE
- BLK-006 Pull Request #1 Merge: NOT AUTHORIZED

## Final Disposition

PO-GOV-AUTH-001 establishes the prospective foundational authority required to
record and execute a narrowly controlled governance-bootstrap process. The
immediate authorized action is limited to this dedicated branch, one validated
commit, and branch push. Pull request creation, Bootstrap Merge Authorization,
merge execution, post-merge verification, exception adoption, and BLK-006
reassessment remain separate controlled stages.
