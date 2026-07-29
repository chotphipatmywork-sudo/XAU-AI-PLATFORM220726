# BSC-001 Backtest Schema Contract

Version: 1.0.0

Status: Draft — Specification only

Document Type: Offline backtest schema contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define canonical fields for backtest events and summary evidence.

## Required Fields

`record_id`, `symbol`, `timestamp`, `decision_id`, `event_id`, `event_type`, `side`, `price`, `quantity`, and `status`.

## Rules

Fields use deterministic types and ordering. Timestamps are UTC. Prices and quantities must be finite and non-negative where applicable.

## Identity

Each event has a unique `event_id` and preserves its source decision and record identities.

## Acceptance Criteria

Schema, chronology, identity, and partition checks pass without silent coercion.

## References

BEC-001, DIC-001, DIS-001, DVC-002, DMS-002, RDS-001, DPC-001, and DAC-001.
