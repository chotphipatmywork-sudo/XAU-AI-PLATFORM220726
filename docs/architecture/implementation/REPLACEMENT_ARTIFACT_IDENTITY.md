# Replacement Artifact Identity Record

Version: 1.0.0

Status: Identity frozen; source pending; execution not authorized

Document Type: Replacement Evidence Identity Record

Architecture Baseline: ABR-1.0 (Frozen)

Effective governance baseline commit: `a7b324e5d2b0ebe7b2c91a522ae2e9a56f554685`

## Approved Replacement Identity

| Field | Approved value |
| --- | --- |
| Replacement Project ID | `IMP-100-REPLACEMENT-001` |
| Replacement Run ID pattern | `IMP-100-REPLACEMENT-001-RUN-YYYYMMDDTHHMMSSZ` |
| Artifact family | `IMP-100 Controlled Replacement Canonical Artifact` |
| Artifact base name | `imp100_replacement_canonical_artifact_v1` |
| Identity schema version | `1.0.0` |
| Artifact schema version | `1.0.0` |
| Manifest schema version | `1.0.0` |
| Governance baseline | `a7b324e5d2b0ebe7b2c91a522ae2e9a56f554685` |

This identity represents a replacement artifact. It does not recover, restore, recreate identically, or overwrite the historical lost artifact.

## Naming Conventions

| Item | Approved pattern |
| --- | --- |
| Artifact filename | `imp100_replacement_canonical_artifact_v1_<RUN_ID>.<approved-extension>` |
| Manifest filename | `imp100_replacement_manifest_v1_<RUN_ID>.json` |
| Generation log | `imp100_replacement_generation_log_<RUN_ID>.log` |
| Validation report | `imp100_replacement_validation_report_<RUN_ID>.json` |
| Reproducibility record | `imp100_replacement_reproducibility_<RUN_ID>.json` |

## Canonical Paths

Canonical storage root:

`C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts`

| Purpose | Canonical path |
| --- | --- |
| Accepted artifact | `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\accepted` |
| Failed runs | `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\failed_runs` |
| Manifests | `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\manifests` |
| Generation logs | `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\generation_logs` |
| Validation | `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\validation` |
| Reproducibility | `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\reproducibility` |
| Local backup staging | `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts\backups` |

The local backup-staging directory is not an independent backup.

## Historical Artifact Separation

Historical lost-artifact SHA-256:

`F2D45BAB50AE56933D7634151897A815DCDFD58E1AC48C0AD6F8E08779423E85`

Rules:

- Do not assign the historical hash to the replacement.
- Do not use it as an expected replacement hash.
- Do not claim byte-for-byte identity or recovery.
- Do not overwrite or reinterpret historical IMP-100 evidence.
- The replacement receives its own SHA-256 after authorized generation.
- The replacement manifest must classify the artifact as `REPLACEMENT`.

## Source Identity State

The following remain pending and must not be guessed or fabricated:

- Source dataset identity.
- Source dataset path.
- Source dataset version.
- Source dataset SHA-256.
- Source configuration SHA-256.
- Replay contract SHA-256.
- Generator implementation commit.
- Generator implementation SHA-256, where applicable.

These fields may be populated only after source discovery, verification, and Project Owner approval.

## Run Identity Rules

Each authorized generation attempt receives one unique immutable Run ID.

- Use UTC.
- Follow the approved Run ID pattern.
- Generate it once at the start of an authorized run.
- Reuse it consistently across artifact, manifest, logs, validation, and reproducibility records.
- Never reuse it after a failed or interrupted run.
- Never rename it after generation.
- Keep it attached to failed-run evidence.

## Acceptance-State Rules

Allowed lifecycle states:

- `IDENTITY_FROZEN`
- `SOURCE_PENDING`
- `SOURCE_APPROVED`
- `AUTHORIZED_FOR_GENERATION`
- `GENERATED`
- `VALIDATION_FAILED`
- `VALIDATION_PASSED`
- `ACCEPTED`
- `REJECTED`
- `ARCHIVED`

Current lifecycle state:

`IDENTITY_FROZEN`

This task must not advance the state beyond `SOURCE_PENDING`.

## Governance Baseline

| Item | Status |
| --- | --- |
| Repository branch | `main` |
| Governance baseline commit | `a7b324e5d2b0ebe7b2c91a522ae2e9a56f554685` |
| Canonical storage root | `C:\Users\poowa\Documents\Codex\XAU-AI-PLATFORM-replacement-artifacts` |
| Project Owner storage write test | `PASS` |
| Independent backup | `PENDING` |
| Execution Authorization | `NOT AUTHORIZED` |

## Project Owner Approval Record

| Role | Decision | Reference |
| --- | --- | --- |
| Project Owner | `APPROVED` | Single Owner governance decision; identity freeze approval |

## Identity Freeze Decision

The replacement identity, naming conventions, schema versions, and canonical paths are frozen for subsequent source-identity work. This decision does not authorize source discovery, dataset generation, replay, artifact generation, model training, Runtime use, or deployment.

## Validation Results

- Exactly one replacement Project ID is defined: PASS.
- Artifact and manifest naming patterns are deterministic: PASS.
- Canonical paths match the approved storage structure: PASS.
- Historical and replacement identities are separated: PASS.
- Replacement generation hash is not pre-populated: PASS.
- Source hashes are not fabricated: PASS.
- Artifact generated: NO.
- Replay executed: NO.
- Execution authorization granted: NO.
- Runtime and protected modules modified: NO.

## Final Status

Identity state: `IDENTITY_FROZEN`

Execution Authorization: `NOT AUTHORIZED`

No dataset, replay, artifact, manifest with generation results, commit, or push was created by this identity-freeze update.
