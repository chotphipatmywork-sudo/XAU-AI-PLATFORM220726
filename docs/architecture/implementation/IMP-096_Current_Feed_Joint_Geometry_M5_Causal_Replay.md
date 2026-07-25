# IMP-096 Current-Feed Joint Geometry M5 Causal Replay

Version: 1.0.0

Date: 2026-07-24

Status: Requests prepared and hash-verified; compile pending

Architecture Baseline: ABR-1.0

## Contract

The IMP-095 research lead is frozen as M5 Stop 2 plus M15 Target 1. No geometry
or gate may change. The 76 mature Train observations are exported as M5 paths
to resolve intrabar ordering.

This lead was selected after Train frontier inspection. The replay is therefore
diagnostic, not independent confirmation. Validation/Test, Runtime, Risk,
Execution, Forward testing, and Deployment remain locked and NO-GO.

## Prepared evidence

- Frozen requests: 76.
- Request SHA-256:
  `E454343B9AF390ADB8860DEB317A126403F277818B1DA9D387E5DAAD6A7A9D5C`
- Manifest SHA-256:
  `01EEA443939B9EBE5B0C017525461B348929A11161966C5EFB2E6F8C4233F754`
- MT5 copy: hash-verified.

The first compile launch did not create a log because the new script had not
yet used the repository's path-safe `Start-Process` argument form. The script
has been corrected. Final compile evidence remains pending and the exporter
must not be run until `0 errors, 0 warnings` is confirmed.
