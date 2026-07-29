# SRC-001 Source Data Contract

Version: 1.0.0

Status: Draft — Approval required; source acquisition not authorized

Architecture Baseline: ABR-1.0 (Frozen)

Document Type: Controlled Research Regeneration source contract

## Purpose

This contract defines canonical source-data requirements for the `CONTROLLED_RESEARCH_REGENERATION` track. No dataset generation is permitted without an approved source.

## Scope

This contract governs source identity, provenance, integrity, acquisition, normalization, quality, chronology, validation, acceptance, and rejection for future offline research. It does not modify historical IMP-099, IMP-100, or IMP-101C contracts and does not alter Runtime or protected modules.

## Source Approval Policy

Each source requires a documented Source ID, complete provenance, declared configuration, integrity evidence, validation results, and Project Owner approval before use. Approval is limited to the named symbol, timeframe, time range, provider, acquisition method, and version.

No dataset generation, replay, feature generation, label generation, or training may begin before source approval.

## Supported Data Sources

Sources may be used only when their provider, delivery format, timestamp semantics, price fields, symbol mapping, and licensing or access basis are documented. A source may be broker-exported, locally archived, or another explicitly approved deterministic source. An unverified or undocumented source is not supported.

## Source Identity

Every source receives a unique, immutable Source ID. The identity record must include provider, instrument, timeframe, coverage range, format, schema version, acquisition configuration, and source version. Historical datasets and source identities shall never be reused silently.

## Source Provenance

Immutable provenance must identify the original provider or archive, acquisition date and method, repository or external location, operator or process, configuration, timezone, symbol mapping, and parent source where applicable. Every source must have immutable provenance before approval.

## Source Integrity

The accepted source record must include exact byte size where available, file format, schema evidence, record count, and SHA-256. Hashes are calculated only during an authorized source-validation operation; this contract assigns no generation-time values.

## Source Versioning

Source versions use an explicit semantic or provider version. Any byte, schema, provider, configuration, coverage, or normalization change creates a new Source ID or approved source version. Existing accepted sources are not overwritten.

## Data Acquisition Rules

Acquisition is offline and controlled. The operator must record the exact command or procedure, inputs, output location, start and completion times, exit status, and environment. Acquisition must not access Validation or Test contents and must not create runtime dependencies.

## Data Quality Requirements

An approved source must satisfy declared schema, non-empty coverage, valid timestamps, valid numeric fields, consistent symbol and timeframe, deterministic ordering, and documented record accounting. Quality failures are retained in the validation report and block acceptance until dispositioned.

## Time Synchronization

Timestamps must use the provider’s documented clock semantics and a single declared precision. Records must be ordered deterministically. Any clock conversion, bar-boundary interpretation, or alignment operation must be versioned and recorded as transformation provenance.

## Timezone Rules

The source timezone and the normalized research timezone must be explicitly recorded. Conversions must be deterministic, preserve the instant in time, and account for daylight-saving rules where applicable. An unknown timezone fails validation.

## Symbol Naming Rules

The source symbol, provider symbol, and normalized research symbol must be recorded together. Symbol aliases require an explicit mapping record. A symbol mismatch or undocumented suffix, contract, or point-value convention rejects the source.

## Timeframe Rules

The timeframe must be declared using the repository’s canonical notation and must match the approved research contract. Aggregation from a lower timeframe must record the source timeframe, boundary rule, and ordered transformation. Unapproved resampling is prohibited.

## Missing Data Policy

Missing records, bars, fields, or intervals must be detected, counted, and classified. No missing source data may be silently imputed. Any approved handling must be declared in the source and dataset contracts; otherwise the source fails closed.

## Duplicate Data Policy

Duplicate timestamps, identifiers, or source records must be detected and reported. Duplicates may be removed only by an approved deterministic rule recorded in provenance. Silent deduplication is prohibited.

## Data Correction Policy

Corrections never overwrite an accepted source. A correction creates a new source version and Source ID, preserves the prior evidence, records the reason and operator, and repeats validation and approval.

## Source Validation

Validation must verify identity, provenance, schema, format, byte and hash evidence, chronology, timezone, symbol, timeframe, missing-data accounting, duplicate handling, and deterministic serialization. Validation output must identify the validator version, inputs, checks, failures, warnings, and exit status.

## Acceptance Criteria

A source is accepted only when:

- Its Source ID is unique and immutable.
- Provenance is complete and immutable.
- Schema, format, symbol, timeframe, timezone, and coverage are approved.
- Integrity and quality validation passes.
- Corrections, missing data, and duplicates have approved dispositions.
- The Project Owner records approval.

Every approved source is frozen after acceptance.

## Rejection Criteria

Reject a source for missing or mutable provenance, unknown identity, unverifiable integrity, invalid schema or chronology, undocumented timezone or symbol mapping, unresolved missing or duplicate data, unauthorized correction, or any failed mandatory validation check.

## Fail-Closed Rules

The workflow must stop when source identity, provenance, configuration, hash evidence, timezone, chronology, partition boundary, or approval is unavailable or contradictory. No fallback source, silent historical reuse, inferred value, or undocumented correction is allowed.

## Responsibilities

- Project Owner: approves, rejects, and freezes source identities.
- Research owner: prepares the source record and acquisition evidence.
- Technical reviewer: reviews schema, integrity, chronology, and reproducibility.
- Validator: executes the approved checks and preserves reports.
- Implementer: consumes only approved source contracts and must not bypass gates.

## References

- [RFB-001 Research Foundation Blueprint](RFB-001_RESEARCH_FOUNDATION_BLUEPRINT.md)
- [RDR-001 Research Track Decision Record](RDR-001_RESEARCH_TRACK_DECISION_RECORD.md)
- [MARKDOWN_STANDARD.md](../standards/MARKDOWN_STANDARD.md)
- [ABR-1.0 Architecture Freeze](../project/ARCHITECTURE_FREEZE.md)

## Final Status

SRC-001 is documentation only. Source acquisition, dataset generation, replay, training, runtime changes, and protected-module changes remain unauthorized.
