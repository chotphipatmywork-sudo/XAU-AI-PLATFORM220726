# BRC-001 Backtest Result Contract

Version: 1.0.0

Status: Draft — Specification only

Document Type: Offline backtest result contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define causal trade lifecycle and result evidence after entry events.

## Scope

Offline research only. Results must not authorize Risk, Execution, or live orders.

## Lifecycle

`ENTRY` → `OPEN` → `EXIT` → `CLOSED`

Valid exits are `STOP`, `TARGET`, `TIMEOUT`, or `END_OF_DATA`. Every closed trade has exactly one exit reason.

## Costs

Spread, slippage, commission, and fees are explicit configuration inputs and must never be silently assumed.

## Acceptance

Every result links to its entry, exit, decision, source record, and configuration identities.

## References

BEC-001, BSC-001, BVC-001, BMS-001, DIC-001, and DAC-001.
