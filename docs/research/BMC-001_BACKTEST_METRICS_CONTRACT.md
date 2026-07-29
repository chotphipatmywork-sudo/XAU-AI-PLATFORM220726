# BMC-001 Backtest Metrics Contract

Version: 1.0.0

Status: Draft — Specification only

Document Type: Offline backtest metrics contract

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define deterministic trade-level and aggregate metrics.

## Required Metrics

Trade PnL, net PnL, return, win/loss classification, trade count, win rate, average win, average loss, profit factor, maximum drawdown, and exposure duration.

## Rules

Metric formulas, decimal precision, cost treatment, empty-set behavior, and denominator rules must be versioned. Undefined metrics fail closed rather than becoming zero.

## Acceptance

Repeated calculation over identical closed trades produces identical values and serialized output.

## References

BRC-001, BVC-001, EFC-001, ESC-001, and EMS-001.
