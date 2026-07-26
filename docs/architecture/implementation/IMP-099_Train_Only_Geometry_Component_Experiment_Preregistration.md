# IMP-099 Train-only Geometry Component Experiment Preregistration

Status: Design completed and validated; experiment not executed

Architecture Baseline: ABR-1.0 (Frozen)

Baseline: IMP-098 at commit
`1a2dc715bd118dd607659162dafdd8640112b7cc`

## Purpose

IMP-099 preregisters one bounded Train-only experiment to isolate the two
mechanically plausible IMP-098 causes: selected Stop depth and available Target
distance. It does not execute the experiment.

## Frozen factorial design

| Arm | Stop | Target | Purpose |
|---|---|---|---|
| CONTROL | `m5_stop_2` | `m15_target_1` | Frozen IMP-097 geometry |
| STOP_ONLY | `m5_stop_1` | `m15_target_1` | Isolate reduced Stop depth |
| TARGET_ONLY | `m5_stop_2` | `m15_target_2` | Isolate additional Target distance |
| COMBINED | `m5_stop_1` | `m15_target_2` | Measure combined components |

Entry, cost formula, Minimum RR `2.0`, and source artifacts remain frozen.

## Hypotheses

1. `STOP_ONLY` improves the paired RR pass rate over CONTROL through reduced
   invalidation distance.
2. `TARGET_ONLY` improves the paired RR pass rate over CONTROL through increased
   available Target distance.
3. COMBINED improves the paired RR pass rate over CONTROL through both
   components.

## Analysis contract

- Primary population: common support across all four arms.
- Secondary population: all 597 Train requests, with missing/invalid geometry
  reported and never imputed.
- Primary metric: cost-adjusted RR pass rate at frozen `2.0R`.
- Paired test: exact McNemar.
- Effect interval: paired bootstrap 95% with fixed seed `98099`.
- Three planned contrasts; Bonferroni alpha `0.016666666666666666`.
- Context results are descriptive only and cannot create filters.

## Train-only experiment gate

A future arm must satisfy all of:

- at least 200 common-support records;
- corrected statistical significance;
- at least 5 percentage-point absolute pass-rate improvement;
- at least 80% geometry coverage relative to CONTROL;
- improvement in both BUY and SELL.

Permitted decisions are `NO_GO`, `CONTINUE_DIAGNOSTIC_RESEARCH`, or
`GO_TRAIN_ONLY_REPLAY`. None authorizes Runtime or deployment.

## Validation

- Focused safety-mutation test: PASS.
- Frozen source hashes: PASS.
- Four-arm identity: PASS.
- Three-contrast correction: PASS.
- Validation/Test sealed: PASS.
- Experiment executed: false.
- Runtime/Protected Modules changed: false/false.
- Deployment authorized: false.
- Research Scorecard: `NO_GO_TRAIN`; Overall Readiness `49.0`.
- Delta Report versus IMP-098: `0.0` for every score dimension.
- Baseline promotion allowed: false.
- Research Scorecard SHA-256:
  `D4177340FBF37E13275F0BA2EF33EA8E096B23F57626B651EDDC07A1932BF69A`.
- Preregistration SHA-256:
  `E0A9B1F5D342C2527AC929557CFCB961E9C8BF71B4193A20234AE252A33F17FA`.
- Validation SHA-256:
  `EB7F71346DEE3720A3681AB41DC40453082865B128D7CDD39707B1684CAF7EA3`.

## Limitations

- `m15_target_2` availability may reduce common support; this is measured, not
  imputed.
- The experiment tests existing ladder levels only.
- It cannot establish structure age or late-entry timing.
- It is not parameter optimization and cannot create a production candidate.

## Gate Decision

Decision: `READY_TO_RUN_TRAIN_ONLY_EXPERIMENT`.

This authorizes only a separately implemented execution of the preregistered
analysis. It does not authorize changing the design after results are known.
