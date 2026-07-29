# RDR-001 Research Track Decision Record

Version: 1.0.0

Status: Draft — Approval required; execution not authorized

Architecture Baseline: ABR-1.0 (Frozen)

Decision ID: RDR-001

Decision Date: 2026-07-29

Decision Owner: Project Owner

Reference: [RFB-001 Research Foundation Blueprint](RFB-001_RESEARCH_FOUNDATION_BLUEPRINT.md)

## Purpose

This record establishes the `CONTROLLED_RESEARCH_REGENERATION` track as the governed lineage for future offline research. It does not authorize source acquisition, data export, replay, dataset generation, training, or production use.

## Context

The historical IMP-099, IMP-100, and IMP-101C research activities are closed. The original historical generated artifacts are unavailable, and their recorded results remain evidence only. The repository now requires a separate, controlled lineage for any future research regeneration.

## Problem Statement

Future research must be reproducible and traceable without conflating newly generated evidence with historical work or introducing dependencies into the ABR-1.0 runtime architecture.

## Decision

The project establishes `CONTROLLED_RESEARCH_REGENERATION` as a distinct offline research track. Every future research object must receive a new identity lineage, versioned contracts, provenance metadata, validation evidence, and an explicit approval record before acceptance or freeze.

Governance takes precedence over implementation. No implementation may bypass an approved policy, standard, contract, validation gate, or acceptance decision.

## Scope

This decision governs:

- Research-track identity and lineage.
- Offline source, dataset, replay, experiment, model, evaluation, manifest, and artifact governance.
- Versioned contracts, provenance, validation, acceptance, freeze, archive, and backup controls.
- Separation of historical evidence from new research outputs.

The track must preserve ABR-1.0 boundaries and remain independent of Runtime, Brain, AI Runtime, Risk, Execution, Learning, feature, label, and deployment behavior.

## Out of Scope

- Recovery or byte-for-byte recreation of historical artifacts.
- Modification of IMP-099, IMP-100, or IMP-101C contracts or documents.
- Source acquisition or market-data export.
- Dataset, feature, label, replay, model, or artifact generation.
- Training, deployment, live inference, or production use.
- Opening or inspecting Validation/Test dataset contents.
- Changes to Execution Authorization.

## Historical Boundary

Historical IMP-099, IMP-100, and IMP-101C remain closed and read-only. Historical artifacts and results are evidence only. New research must use a new identity lineage and must never claim recovery, restoration, or byte-for-byte recreation of historical work. No recovery claim is permitted.

## Consequences

Positive consequences:

- New research can be independently identified and audited.
- Provenance and reproducibility become acceptance requirements.
- Historical evidence remains protected from reinterpretation.
- Research work remains isolated from the canonical runtime flow.

Operational consequences:

- New source, configuration, dataset, experiment, and artifact contracts are required before generation.
- Validation, independent backup, acceptance, and freeze gates add mandatory work.
- Missing provenance or unresolved identity prevents acceptance.

## Risks

| Risk | Control |
| --- | --- |
| New output is misrepresented as historical recovery | Separate track, identities, manifests, and explicit no-recovery rule |
| Research code changes protected runtime boundaries | ABR-1.0 and ADR review before any boundary or contract change |
| Dataset leakage across partitions | Explicit partition identities, sealing, chronology, and validation gates |
| Incomplete provenance prevents reproduction | Fail-closed metadata and acceptance requirements |
| Internal backup is mistaken for independent backup | Separate approval and verification of an independent destination |

## Approval Status

Decision status: **PENDING APPROVAL**

Approval authority: Project Owner, under the current Single Owner Project governance decision.

Approval of this record may authorize progression to preparation of foundation contracts only. It does not authorize source acquisition, market-data export, replay, dataset generation, feature or label generation, training, model creation, deployment, or execution.

## Final Status

RDR-001 is a documentation-only decision record. Existing files and contracts remain unchanged.
