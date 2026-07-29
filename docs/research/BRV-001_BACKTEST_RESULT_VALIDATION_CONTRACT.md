# BRV-001 Backtest Result Validation Contract

Version: 1.0.0

Status: Draft — Specification only

Document Type: Offline backtest result validation contract

Architecture Baseline: ABR-1.0 (Frozen)

## Validation Rules

Validate one entry and one exit per closed trade, causal exit chronology, valid price conventions, explicit costs, PnL arithmetic, accounting totals, unique identities, deterministic order, finite metrics, and manifest hashes.

## Fail-Closed Rules

Reject overlapping trades where prohibited, missing exits, negative or non-finite prices, implicit costs, future-bar access, undefined denominators, and mismatched parent identities.

## Acceptance

All mandatory checks pass and validation evidence is independently backed up before freeze.

## References

BRC-001, BMC-001, BSC-001, BVC-001, and DAC-001.
