# ELC-001 Environment Lock Contract

Version: 1.0.0

Status: Draft — Approval required; execution not authorized

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

This contract defines the environment identity required for reproducible `CONTROLLED_RESEARCH_REGENERATION` work. It applies only to offline research and does not modify Runtime or protected modules.

## Operating System

Record operating-system name, edition, version, architecture, locale, installed updates relevant to execution, and environment identity. An unrecorded or materially different operating system fails the reproducibility gate.

## Python Version

Record the exact Python implementation and version used by every Python generator, validator, or evidence tool. Version ranges are insufficient for an accepted run.

## Package Lock

Record an exact package lock, including package names, versions, and hashes where supported. `training/requirements.txt` is an existing dependency reference; it is not by itself an immutable environment lock.

## Git Commit Requirement

Every run must identify the exact Git commit used by the generator and validator. A missing or unresolved commit fails closed.

## Working Tree Requirement

The working-tree state must be recorded. A clean tree is required unless all uncommitted paths are explicitly listed, proven irrelevant to output, and approved before execution.

## Environment Variables

Record every environment variable that can affect source selection, paths, serialization, randomness, locale, timezone, or computation. Secrets must be represented by stable redacted identifiers, never copied into evidence.

## Locale

Record process locale and encoding. Locale-dependent parsing or formatting must be fixed explicitly and validated.

## Timezone

Record system and process timezone. All timestamp conversions must use the declared timezone and deterministic rules from SRC-001 and DPC-001.

## Random Seed Policy

Every stochastic operation requires an explicit recorded seed. If no randomness is intended, the run must state that fact. An unrecorded seed or nondeterministic fallback fails closed.

## Fail-Closed Rules

Execution must stop when operating-system identity, runtime or package versions, Git commit, working-tree state, relevant environment variables, locale, timezone, or random seed information is missing, contradictory, or unverifiable.

## References

- [RFB-001 Research Foundation Blueprint](RFB-001_RESEARCH_FOUNDATION_BLUEPRINT.md)
- [RDR-001 Research Track Decision Record](RDR-001_RESEARCH_TRACK_DECISION_RECORD.md)
- [SRC-001 Source Data Contract](SRC-001_SOURCE_DATA_CONTRACT.md)
- [MMS-001 Metadata Manifest Schema](MMS-001_METADATA_MANIFEST_SCHEMA.md)
- [DLC-001 Dataset Lifecycle Contract](DLC-001_DATASET_LIFECYCLE_CONTRACT.md)
- [DPC-001 Dataset Partition Contract](DPC-001_DATASET_PARTITION_CONTRACT.md)

## Final Status

ELC-001 is documentation only. It does not authorize acquisition, generation, replay, training, or production use.
