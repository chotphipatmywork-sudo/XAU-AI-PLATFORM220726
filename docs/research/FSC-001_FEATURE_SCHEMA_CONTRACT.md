# FSC-001 Feature Schema Contract

Version: 1.0.0

Status: Draft — Approval required; training not authorized

Document Type: Research feature schema contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the versioned, deterministic feature columns produced from canonical research records.

## Schema

Identity columns are `record_id`, `symbol`, and `timestamp`. Required OHLC inputs are `open`, `high`, `low`, and `close`. Initial feature columns, in exact order, are `return_1`, `return_3`, `candle_range`, `candle_body`, `upper_wick`, `lower_wick`, `body_ratio`, `range_ratio`, `rolling_mean`, and `rolling_std`.

All feature values are finite decimal numbers or the declared warm-up null. No labels are produced.

## Invariants

Identity values and row count are preserved. Feature ordering is fixed by this document. Calculations use only the current and preceding rows; future rows are never read.

## Versioning and Acceptance

Any column, formula, type, ordering, null, or serialization change requires a new schema version and review. Acceptance requires FSC, FEC, FMC, and FVC validation to pass.

## References

RFB-001, RDR-001, SRC-001, MMS-001, DLC-001, DPC-001, ELC-001, DAC-001, SAP-001, and RDS-001.
