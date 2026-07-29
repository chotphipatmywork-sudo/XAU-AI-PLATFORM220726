# BMS-001 Backtest Manifest Specification

Version: 1.0.0

Status: Draft — Specification only

Document Type: Offline backtest manifest specification

Architecture Baseline: ABR-1.0 (Frozen)

## Purpose

Define provenance and identity metadata for each backtest evidence set.

## Required Metadata

The manifest must include schema version, source identities and hashes, decision-inference identity and hash, replay configuration and hash, output hash, record counts, validation report identity, Git commit, environment identity, generation command, acceptance status, and storage location.

## Determinism

Serialization uses sorted JSON keys, UTF-8, LF newline, stable timestamps for evidence metadata, and exact output-byte hashing.

## Freeze

Accepted manifests and outputs are immutable and independently backed up.

## References

BEC-001, BSC-001, BVC-001, DMS-002, MMS-001, DLC-001, ELC-001, and DAC-001.
