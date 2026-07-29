# BEC-001 Backtest Engineering Contract

Version: 1.0.0

Status: Draft — Specification only

Document Type: Offline backtest engineering contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define the controlled offline backtest boundary for accepted inference and decision evidence.

## Scope

Backtest only; no broker, Runtime, Risk, Execution, or live order integration.

## Inputs

Frozen market/replay data, accepted decision-inference records, configuration, and manifests.

## Outputs

Deterministic trade-event evidence and a manifest. Outputs are research evidence only.

## Invariants

Chronology is causal, inputs are immutable, and every event retains its source identity.

## Validation

Reject missing identities, duplicate events, look-ahead, invalid prices, non-deterministic ordering, and hash mismatch.

## Acceptance Criteria

Repeated runs produce identical bytes and hashes; all provenance and accounting checks pass.

## References

RFB-001, RDS-001, DIC-001, DIS-001, DVC-002, DMS-002, ELC-001, and DAC-001.
