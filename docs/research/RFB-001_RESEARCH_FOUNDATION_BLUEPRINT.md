# RFB-001 Research Foundation Blueprint

Version: 1.0.0

Status: Draft — Foundation approval required; execution not authorized

Architecture Baseline: ABR-1.0 (Frozen)

Document Type: Controlled Research Regeneration governance blueprint

## Purpose

This blueprint defines the constitution of the `CONTROLLED_RESEARCH_REGENERATION` track. It establishes authority, identity, data, validation, acceptance, and reproducibility rules for future offline research while preserving the historical research record and the ABR-1.0 runtime boundary.

## Part 0 Research Principles

- Research is offline, evidence-driven, versioned, and fail-closed.
- Historical IMP-099, IMP-100, and IMP-101C are closed, read-only evidence.
- A replacement or regenerated object receives a new identity and must never claim recovery or byte-for-byte recreation.
- Validation and Test partitions remain sealed unless separately authorized.
- Research changes do not alter Runtime, Brain, AI Runtime, Risk, Execution, Learning, features, labels, or deployment behavior.
- Missing provenance, ambiguous inputs, or failed validation blocks acceptance.

## Part I Vision

The research foundation provides a traceable path from approved research questions to reproducible, independently verifiable evidence. It supports controlled regeneration without creating an implicit production dependency or an ungoverned platform.

## Part II Research Architecture

The research architecture is an offline boundary around existing approved contracts and implementations. Dependencies flow from versioned source and configuration contracts to generators, validators, manifests, and accepted evidence. No research component may call the canonical runtime path or introduce a reverse or circular dependency.

The authority hierarchy is:

```text
Research Constitution
    → Policies
        → Standards
            → Contracts
                → Implementations
                    → Generated Artifacts
```

Historical contracts remain unchanged. Any adaptation requires explicit review and a versioned contract.

## Part III Identity System

Each new lineage must have distinct, deterministic identifiers for:

- Research Track
- Data Snapshot
- Feature Set and version
- Label Set and version
- Dataset and version
- Experiment
- Run
- Replay
- Model
- Evaluation
- Acceptance Artifact
- Manifest

Naming patterns may be specified by policy, but generation-time identifiers, timestamps, and hashes are not assigned by this document. Relationships must be recorded in the manifest and must resolve to exactly one versioned parent object.

## Part IV Data Governance

Research objects follow this lifecycle:

```text
Define → Approve → Implement → Validate → Accept → Freeze → Archive
```

`Define` records intent and contracts. `Approve` authorizes implementation scope. `Implement` creates only the approved offline object. `Validate` applies automated checks. `Accept` requires the designated approval authority. `Freeze` makes the accepted bytes and metadata immutable. `Archive` preserves retrieval and provenance.

Datasets must record source identity, schema, transformation steps, partition boundaries, counts, hashes, environment, and access status. Train, Validation, and Test partitions require distinct identities and explicit time boundaries. Train may support fitting after approval; Validation and Test remain sealed by default. No dataset is Train-eligible merely because it was generated.

## Part V Research Governance

Research questions, hypotheses, preregistrations, contracts, and acceptance decisions are separate records. The Project Owner is the approval authority under the current single-owner governance decision. Approval does not authorize source acquisition, replay, generation, training, or production use unless the applicable execution record expressly grants it.

Historical IMP-099, IMP-100, and IMP-101C remain closed and read-only. Their results are evidence only and cannot be silently reclassified as new-track outputs.

## Part VI AI Governance

Feature definitions, implementations, configurations, and versions are distinct objects. Label definitions, implementations, configurations, and versions are also distinct. Future catalogs must record causality, lookback, warm-up, fitting partition, missing-value policy, leakage risk, barrier rules, timeout, collision handling, and validation status.

No new feature, label, model, or training policy is created by this blueprint. Existing canonical feature and label semantics remain governed by their approved contracts.

## Part VII Validation

Validation is independent, deterministic, and fail-closed. It must verify identity, schema, source provenance, partition accounting, chronology, leakage controls, serialization, reproducibility metadata, and output hashes. Failed checks produce a rejected or quarantined run; records may not be silently omitted.

Validation and Test contents must remain unopened during foundation work. Validators must report their identity, version, input hashes, configuration hashes, results, failures, warnings, and exit status.

## Part VIII Acceptance

Acceptance requires a complete manifest, passing validation, reproducibility evidence, approved storage, and Project Owner approval. Accepted artifacts are stored in the approved accepted-artifact location and frozen by exact bytes and hashes. An internal backup staging directory is not an independent backup unless a separate destination is approved and verified.

Acceptance does not change Execution Authorization, which remains `NOT AUTHORIZED` unless separately approved.

## Part IX Reproducibility

Every accepted run must retain the operating system, runtime and package versions, Git commit and working-tree state, source and configuration hashes, relevant environment variables, locale, timezone, random seeds, ordered commands, exit codes, timestamps, output hashes, and storage locations. Missing information that can affect output causes fail-closed behavior.

## Part X Future Expansion

Future work may add approved source contracts, manifest tooling, experiment registry support, feature and label catalogs, independent backup automation, and training or replay workflows. Each addition requires its own specification, review, validation, and approval. Expansion must remain minimal, offline, versioned, and independent of protected runtime modules.

## Review and Result

This document creates governance guidance only. It does not modify existing contracts, create datasets, execute replay, train models, change Runtime, or alter protected modules.

## Document End

RFB-001 remains pending foundation approval.
