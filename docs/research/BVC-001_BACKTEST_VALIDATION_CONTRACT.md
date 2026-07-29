# BVC-001 Backtest Validation Contract

Version: 1.0.0

Status: Draft — Specification only

Document Type: Offline backtest validation contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define fail-closed validation for backtest evidence.

## Validation Rules

Validate input hashes, schema, identity continuity, event chronology, causal bar access, duplicate events, accounting totals, deterministic ordering, and manifest consistency.

## Leakage Controls

An event may use only data available at or before its permitted evaluation timestamp. Future bars, labels, or outcomes are prohibited.

## Acceptance

All mandatory checks pass, warnings are dispositioned, and evidence is backed up before freeze.

## Prohibited Results

Validation must not grant Risk approval, Execution authority, or Runtime access.

## References

BEC-001, BSC-001, DVC-002, DMS-002, EVC-001, EMS-001, ELC-001, and DAC-001.
