# IMP-100 Train-only Geometry Causal Replay

**Status:** CLOSED - CONTINUE_TRAIN_ONLY_RESEARCH
**Architecture baseline:** ABR-1.0 (Frozen)
**Baseline commit:** `32e044c86691b9e84f8fa54d21e3d20448f27eeb`
**Runtime candidate:** Not created
**Deployment:** Not allowed

## Purpose

Execute the frozen IMP-100 Train-only experiment on deterministic,
outcome-free closed-M5 paths. The replay assigns outcomes for the first time
without accessing Validation/Test data or changing Runtime behavior.

## Frozen baseline

- IMP-099 opportunity ledger: 2,388 records.
- Primary common-support opportunities: 362.
- Active replay requests: 685.
- Arms: CONTROL, STOP_ONLY, TARGET_ONLY, COMBINED.
- Minimum RR remains 2.0.
- Maximum replay path: 192 closed M5 bars.
- Validation and Test datasets remain sealed.

| Frozen evidence | SHA-256 |
|---|---|
| Contract | `9D0142D1671E80C1263D93A61E1CB53316EC8E816040B251F477F974540494A9` |
| Active requests | `C4BDA8102E50F266714D99EE0CF27D71540DEA1ADC7DA3757528BC7155B63085` |
| Request manifest | `3DDD49D0C4BCB0239243B654333FE6A6B338BF2E9465B1C858E316D0EE0911A7` |
| Outcome-free M5 export | `5F95AAE3381E3F92879759362D4DAE771D76F13F1FEE02B9414D845A6F520FE6` |
| Export validation | `20FC23DC1876E2D60AD36F8610ADB040F14931C6EAEAAB6D9065A29E34DD642A` |
| Export manifest | `5E5A1CD8396C358B910C97FDD49A5D2904732321C95A24DBBE3F4CFC6E8D8B96` |

## Replay methodology

- Replay each request using only its exported closed-M5 sequence.
- Process bars in chronological order.
- Record Target hit, Stop hit, Timeout, invalid path, or same-bar collision.
- Quarantine Stop/Target collisions occurring in the same M5 bar; do not
  infer intrabar ordering.
- Retain common-support no-trade observations as zero for arm gate metrics.
- Use deterministic circular moving-block bootstrap with seed `20260722`,
  10,000 samples, and block length `ceil(n^(1/3))` with a minimum of 2.
- Apply the frozen 1.0, 1.25, and 1.5 cost-stress multipliers.

## Replay result

All 685 requests were processed with no missing or duplicate replay.

| Result | Count |
|---|---:|
| Target hit | 114 |
| Stop hit | 567 |
| Same-bar collision quarantined | 4 |
| Timeout | 0 |
| Invalid path | 0 |

Two independent runs produced the same replay-record hash:

`541EC9697EAFF3CF4D2723EAD2EFD1598097EACC65E22E418C5AE315B18FAE08`

## Per-arm evidence

Primary gate metrics use the frozen 362-opportunity common-support population,
excluding quarantined collisions and retaining no-trade as zero.

| Arm | Replay | Win | Loss | Collision | Effective paths | Mean R | PF | Max DD R | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CONTROL | 76 | 21 | 55 | 0 | 59 | 0.0451 | 1.3887 | 7.4584 | FAIL |
| STOP_ONLY | 195 | 30 | 165 | 0 | 129 | -0.1075 | 0.6398 | 40.3837 | FAIL |
| TARGET_ONLY | 146 | 31 | 114 | 1 | 137 | 0.0026 | 1.0087 | 22.0078 | FAIL |
| COMBINED | 268 | 32 | 233 | 3 | 233 | -0.2125 | 0.6261 | 76.5083 | FAIL |

No arm passed all frozen requirements. In particular:

- CONTROL had positive mean R and Profit Factor, but had only 59 effective
  paths, a non-positive bootstrap lower bound, one negative chronological
  block, and failed cost-stress confidence requirements.
- TARGET_ONLY was near break-even at base cost but failed effective sample,
  direction robustness, temporal stability, Profit Factor, bootstrap, and
  cost-stress gates.
- STOP_ONLY and COMBINED had negative expectancy and failed multiple
  robustness gates.

## Validation

- Frozen hashes unchanged: PASS.
- Requests processed: PASS (685/685).
- Unique request mapping: PASS.
- Missing replay: 0.
- Duplicate replay: 0.
- Closed-M5 chronology: PASS.
- Future leakage absent: PASS.
- Same-bar collision quarantine: PASS.
- Invalid paths: 0.
- Two-run replay reproducibility: PASS.
- Focused replay test: PASS.
- Validation/Test isolation: PASS.
- Runtime changed: false.
- Protected Modules changed: false.
- Deployment authorized: false.

Generated evidence is stored under
`training/output/imp100_causal_m5_replay/run_2/`.

## Research Scorecard

- Status: `NO_GO_TRAIN`.
- Research Quality: 100.00.
- Strategy Evidence: 9.43.
- Operational Safety: 100.00.
- Overall Readiness: 49.00 (hard-gate capped).
- Baseline promotion allowed: false.

## Scientific Conclusions

- The geometry changes increased the number of RR-eligible requests, but that
  increase did not translate into robust positive realized-R evidence.
- CONTROL produced a positive point estimate, but its effective sample was
  insufficient and its confidence interval, temporal stability, and cost
  stress evidence did not support qualification.
- TARGET_ONLY was closest to break-even among the experimental geometry arms,
  but its uncertainty included non-positive outcomes and its evidence was not
  stable across direction, chronology, or cost stress.
- STOP_ONLY and COMBINED produced negative common-support expectancy and do
  not justify candidate qualification.
- The IMP-099 eligibility gate therefore did not predict a deployable trading
  advantage when evaluated on causal closed-M5 outcomes.

## Limitations

- Evidence is Train-only.
- Validation/Test and forward-shadow evidence are absent by design.
- Four ambiguous same-bar paths were quarantined rather than resolved.
- No parameter optimization, arm selection, Runtime candidate, or deployment
  authorization was performed.

## Gate Decision

`CONTINUE_TRAIN_ONLY_RESEARCH`

No arm qualifies for Train-only candidate qualification. Runtime remains
unchanged and deployment remains prohibited.

## Recommended Next Research Direction

Continue Train-only diagnostic research on the observed outcome failure modes
before proposing another experiment. Any later milestone must be separately
preregistered, preserve the frozen Minimum RR and causal M5 boundary, keep
Validation/Test sealed, and must not create a Runtime candidate from IMP-100.