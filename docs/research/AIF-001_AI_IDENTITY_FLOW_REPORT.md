# AIF-001 AI Identity Flow Report

Version: 1.0.0

Status: Draft — Read-only audit; AI implementation not authorized

Architecture Baseline: ABR-1.0 (Frozen)

## Identity Creation Points

The contracts define Research Track, Source, Data Snapshot, Dataset, Feature Set, Label Set, Experiment, Run, Replay, Model, Evaluation, Artifact, and Manifest identities. Implementations visibly accept Source/Label/Feature identities and dataset hashes; they do not create the complete hierarchy.

## Identity Propagation Map

```text
Source → Feature/Label Dataset → Training Dataset → Training Run → Evaluation → Model Registry
```

Feature and label pipelines preserve `record_id`, `symbol`, and `timestamp`. Training joins by `record_id` and checks symbol/timestamp agreement. Evaluation and model propagation are contract-only.

## Manifest Linkage

Feature manifests contain source identity and hashes. Label manifests contain source identity and label-set version. Training manifests contain feature/label dataset hashes and partition boundaries. Full links to Research Track, Data Snapshot, Run, Evaluation, and Model IDs are incomplete.

## Validation Ownership

Contracts assign validation to the Validator with Technical Review and Project Owner acceptance. Executable ownership is not independently evidenced, and Python tests cannot be run in this audit environment.

## Missing or Ambiguous Identity Paths

- No complete Experiment, Run, Evaluation, or Model registry implementation.
- No immutable Data Snapshot identity in the reviewed pipelines.
- Manifest fields do not consistently carry schema, configuration, environment, and approval identities.
- Label pipeline accepts a caller-provided source label column; label semantics are not defined by implementation.

## Assessment

Identity flow is **PARTIALLY CONFORMANT** and is not ready for AI implementation.
