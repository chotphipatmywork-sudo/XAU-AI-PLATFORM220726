# BAA-001 Backtest Evidence Authorization Checklist

Version: 1.0.0

Status: Draft — Authorization preparation; evidence generation not executed

Document Type: Controlled offline backtest authorization checklist

Architecture Baseline: ABR-1.0 (Frozen)

## Preconditions

- [x] Backtest contracts and result contracts exist.
- [x] Offline implementations and focused tests exist.
- [x] Runtime, Risk, and Execution boundaries remain unchanged.
- [x] Regression validation has passed.
- [ ] Frozen input dataset identity and SHA-256 recorded.
- [ ] Replay/bar source identity and SHA-256 recorded.
- [ ] Cost configuration approved and hashed.
- [ ] Independent backup destination verified.
- [ ] Project Owner execution authorization recorded.

## Required Evidence Run Inputs

The authorized run must record source identities, source hashes, replay configuration, cost configuration, Git commit, Python environment, generation command, output location, and validation command before execution.

## Required Outputs

The run must produce only offline research evidence: event output, closed-trade result output, metrics, validation report, and complete manifests. No live order, Runtime state, Risk approval, or model artifact may be produced.

## Validation Gate

The run is rejected if any input is missing, hashes mismatch, chronology is non-causal, metrics are undefined, manifests are incomplete, or independent backup is unavailable.

## Freeze Gate

Acceptance requires passing validation, complete provenance, independent backup verification, immutable storage, and Project Owner approval. Until then, outputs remain unaccepted and unfrozen.

## Current Decision

Status: NOT AUTHORIZED FOR EVIDENCE GENERATION

Reason: Required frozen source identities, backup verification, and execution authorization are not present in the repository evidence inspected by BAR-001.

## References

BAR-001, BEC-001, BSC-001, BVC-001, BMS-001, BRC-001, BMC-001, BRV-001, BRM-001, and ABR-1.0.
