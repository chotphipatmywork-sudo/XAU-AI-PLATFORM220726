# IMP-098 Structural Stop-to-Target Imbalance Root Cause

Status: Completed; Train-only experiment may be designed, Runtime remains NO-GO

Architecture Baseline: ABR-1.0 (Frozen)

Baseline: IMP-097 at commit
`1e52a2cebbbbe6a267973c32d72f79fae59e254e`

## Purpose and frozen contract

IMP-098 separates structural Stop construction from available Target distance for
the frozen 459-record IMP-097 RR-evaluable population. It changes no Entry,
Stop, Target, cost, Minimum RR, Runtime behavior, or protected module.

Validation and Test partitions remain sealed. No model is trained and no
Runtime candidate is created.

## Methodology

- Train-only frozen evidence with SHA-256 enforcement.
- Exact parity: 459 records, 383 rejected, 76 accepted.
- Selected geometry remains `m5_stop_2 + m15_target_1`.
- Stop components: Stop-1 distance, selected Stop-2 distance, and the
  Stop-1-to-2 incremental depth.
- Target components: selected Target distance, nearest intervening M5 target,
  obstruction gap, and intervening target count.
- Numeric comparison: rejected versus accepted medians and Cliff's delta.
- Context comparison: fixed groups with two-proportion tests and Bonferroni
  correction.
- Fixed diagnostic rule: oversized Stop if median ratio exceeds `1.25`;
  undersized Target if median ratio is below `0.80`.

## Findings

### Stop and Target diagnosis

- Rejected Stop median: `132.0` points.
- Accepted Stop median: `52.5` points.
- Rejected/accepted Stop median ratio: `2.5143`.
- Stop-distance Cliff's delta: `0.5428`.
- Rejected Target median: `113.0` points.
- Accepted Target median: `301.5` points.
- Rejected/accepted Target median ratio: `0.3748`.
- Target-distance Cliff's delta: `-0.6801`.
- Classification:
  `BOTH_OVERSIZED_STOP_AND_UNDERSIZED_TARGET`.

### Stop construction

- Stop-1 median is `51.0` rejected versus `28.5` accepted points; delta
  `0.3597`.
- Stop-1-to-Stop-2 increment median is `68.0` rejected versus `22.0`
  accepted points; delta `0.4705`.
- The deeper selected Stop contributes materially beyond the nearest
  invalidation proxy.

### Target construction

- Nearest target median is `56.0` rejected versus `93.0` accepted points;
  delta `-0.2889`.
- Selected-target obstruction gap median is `49.0` rejected versus `189.0`
  accepted points; delta `-0.5979`.
- Intervening target count median is `1` rejected versus `3` accepted;
  delta `-0.5020`.
- These values show limited target-side distance. Target-ladder counts remain
  proxies and do not identify a causal opposing structure.

### Entry, direction, session, volatility, and regime

- Entry position within the selected Stop/Target span differs strongly, but
  this quantity is mechanically coupled to RR and cannot independently prove
  late entry.
- Structure age and move-origin timing are absent, so late entry cannot be
  answered causally.
- BUY/SELL, session, trend alignment, trend regime, and volatility regime
  produce no new corrected causal conclusion.
- The `18:00-23:59` association repeats after correction, but remains a
  correlational research hypothesis and must not become a Runtime filter.
- ATR effect is small (`-0.1503`); volatility-change effect is small-to-moderate
  (`0.2572`). Compression or expansion is not established as the primary cause.

## Root Cause Summary

The imbalance is caused by both sides of the geometry:

1. The selected Stop is materially wider, with the Stop-1-to-Stop-2 depth
   increment contributing strongly.
2. The selected Target has materially less available distance.

These components are mechanically plausible causes of low structural RR.
Context factors are associations only. Current provenance cannot determine
structure age or whether Entry occurs late in a developed move.

## Research questions answered

1. Oversized Stop or undersized Target: both.
2. Stop contributors: nearest invalidation distance and additional Stop-2 depth.
3. Target constraints: limited selected/nearest distance; ladder obstruction is
   a proxy.
4. Entry placement: measurable only through an RR-coupled span proxy.
5. Late entry: unanswerable with current provenance.
6. Opposing structure: target ladder suggests limited space but is not causal
   identification.
7. BUY/SELL asymmetry: no corrected actionable conclusion.
8. Session/volatility/regime: no new corrected actionable conclusion.
9. Causality: geometry distances are mechanical; contextual relationships are
   correlational.
10. Future experiment: evidence supports designing one bounded Train-only
    geometry experiment.

## Validation and evidence

- Focused deterministic test: PASS.
- Frozen artifact hashes: PASS.
- IMP-097 population and accounting parity: PASS.
- Train-only boundary: PASS.
- Root-cause report SHA-256:
  `873BCD413B07C7CD6D80B5728DC9152808D51751A4F1DB3D21167FAD37C8CE47`.
- Detail records SHA-256:
  `BBF932A3DCB7789E8AFCA157E467CF6DF3905789543D67BCB334E2FC5813EF86`.
- Validation/Test used: false/false.
- Runtime/Protected Modules changed: false/false.
- Deployment authorized: false.
- Research Scorecard: `NO_GO_TRAIN`; Research Quality `100.0`, Strategy Evidence
  `19.82`, Operational Safety `100.0`, Overall Readiness `49.0`.
- Delta Report versus IMP-097: `0.0` for every score dimension.
- Baseline promotion allowed: false.
- Research Scorecard SHA-256:
  `B89DEC63B6E58F5A08495ADC4D6615016728B9481B570BF458A4AB24F10E9622`.

## Limitations

- Structure age and move-origin timestamps are unavailable.
- Target ladders are obstruction/liquidity-distance proxies.
- Entry span position is not independent of the evaluated ratio.
- No correlation is promoted to a trading rule.
- No parameter or production threshold is tuned.

## Gate Decision

Decision: `GO_TRAIN_ONLY_EXPERIMENT`.

This authorizes only the design of a preregistered, bounded Train-only geometry
experiment that isolates Stop depth and Target availability. It does not
authorize implementation, Runtime changes, a candidate, Validation/Test access,
deployment, or live trading.
