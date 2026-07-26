# PER-100 Post-Experiment Review

**Status:** Evidence review complete
**Scope:** IMP-098, IMP-099, and IMP-100 finalized evidence only
**Runtime:** Unchanged
**Deployment:** Not authorized

## Executive Summary

IMP-099 successfully increased the number of geometries that passed the frozen
Minimum RR eligibility test. That result answered an entry-time geometry
question, not a post-entry profitability question. IMP-100 then replayed the
same frozen requests on causal closed M5 paths and found that no arm produced
robust positive realized-R evidence.

The divergence begins after eligibility: geometry passes the entry-time RR
gate, but the subsequent path reaches the Stop much more often than the
Target. This is directly observed, not inferred from a model. The review does
not establish that one specific component is the sole cause of the losses.

## Final Scientific Conclusion

The increase in RR-eligible geometry was real, but it did not translate into
stable positive realized performance. The divergence occurred after
eligibility and replay entry. Early adverse movement and Stop-first outcomes
dominated the observed paths. The current evidence cannot independently
identify Stop placement, Entry timing, or Market behaviour as the sole cause.
Further Train-only post-entry diagnostics are required before designing
corrective experiments.

## Evidence Set

| Evidence | Location | Relevant conclusion |
|---|---|---|
| IMP-098 report | `docs/architecture/implementation/IMP-098_Structural_Stop_Target_Imbalance_Root_Cause.md` | Rejected geometry had both wider Stop and shorter available Target. |
| IMP-099 preregistration | `docs/architecture/implementation/IMP-099_Train_Only_Geometry_Component_Experiment_Preregistration.md` | Frozen 2x2 hypotheses and eligibility gates. |
| IMP-099 execution scorecard | `training/output/research_scorecard_imp099_execution/research_scorecard.json` | All three eligibility contrasts passed; no deployment authorization. |
| IMP-100 replay report | `docs/architecture/implementation/IMP-100_Train_Only_Geometry_Causal_Replay.md` | No arm passed the realized-outcome strategy gate. |
| IMP-100 replay metrics | `training/output/imp100_causal_m5_replay/run_2/replay_metrics.json` | Per-arm outcomes, holding time, drawdown, direction, chronology, and cost stress. |
| IMP-100 replay validation | `training/output/imp100_causal_m5_replay/run_2/replay_validation.json` | 685/685 mapping, chronology, leakage, collision, and reproducibility checks. |
| IMP-100 strategy gate | `training/output/imp100_causal_m5_replay/run_2/strategy_gate.json` | All four arms failed the frozen strategy gate. |
| IMP-100 research scorecard | `training/output/imp100_causal_m5_replay/run_2/research_scorecard.json` | `NO_GO_TRAIN`; Validation/Test remained sealed. |

## Hypothesis Review

The original IMP-099 hypotheses concerned RR eligibility. They did not
guarantee profitability after entry.

| Hypothesis | Status | Evidence-based interpretation |
|---|---|---|
| STOP_ONLY improves paired RR pass rate over CONTROL. | Supported for eligibility; not supported as a profitability conclusion. | IMP-099 execution notes all three planned contrasts passed the locked eligibility gate. IMP-100 STOP_ONLY mean cost-aware R was -0.1075 on common support and its strategy gate failed. |
| TARGET_ONLY improves paired RR pass rate over CONTROL. | Supported for eligibility; not supported as a profitability conclusion. | The eligibility contrast passed, but TARGET_ONLY mean cost-aware R was 0.0026, with non-positive bootstrap lower bound and failed stability/cost gates. |
| COMBINED improves paired RR pass rate over CONTROL. | Supported for eligibility; rejected as a profitability conclusion. | The eligibility contrast passed, but COMBINED mean cost-aware R was -0.2125, Profit Factor 0.6261, and all four chronological blocks were negative. |

## Geometry Versus Replay

The two phases measure different events:

1. IMP-099 asks whether a proposed Stop/Target geometry satisfies the frozen
   entry-time Minimum RR and cost formula.
2. IMP-100 asks what happens after that entry using chronological closed M5
   bars.

Eligibility expanded to 685 active requests across the four arms, while the
primary replay population retained 362 common-support opportunities. In the
replay, 567 of 685 active requests ended at Stop, 114 at Target, and 4 were
quarantined collisions. Therefore the divergence starts after the geometry
eligibility decision, during path evolution.

The key evidence is the common-support primary metrics:

| Arm | Mean cost-aware R | Profit Factor | Effective paths | Primary Target/Stop/No-trade |
|---|---:|---:|---:|---|
| CONTROL | 0.0451 | 1.3887 | 59 | 17 / 42 / 303 |
| STOP_ONLY | -0.1075 | 0.6398 | 129 | 21 / 108 / 233 |
| TARGET_ONLY | 0.0026 | 1.0087 | 137 | 30 / 107 / 224 |
| COMBINED | -0.2125 | 0.6261 | 233 | 29 / 204 / 126 |

The positive CONTROL point estimate is not robust: it has insufficient
effective paths, a non-positive bootstrap lower bound, a negative
chronological block, and failed cost-stress requirements.

## Stop Analysis

Across the 685 active replay requests, Stop was reached 567 times (82.8%).
Stop frequency by active arm was CONTROL 55/76 (72.4%), STOP_ONLY 165/195
(84.6%), TARGET_ONLY 114/146 (78.1%), and COMBINED 233/268 (86.9%). These are
active-request rates; the paired common-support metrics above remain the
primary comparison because eligibility counts differ by arm.

Stop timing was early:

| Arm | Stop median holding bars | Stop mean holding bars |
|---|---:|---:|
| CONTROL | 2 | 3.873 |
| STOP_ONLY | 1 | 2.624 |
| TARGET_ONLY | 2 | 7.211 |
| COMBINED | 1 | 3.446 |

The common-support maximum loss streaks were 11, 15, 19, and 27 for CONTROL,
STOP_ONLY, TARGET_ONLY, and COMBINED respectively. This establishes loss
clustering in the replay sequence, especially for COMBINED, but does not by
itself identify whether the cause is entry placement, Stop construction, or
market movement.

BUY had 294 Stop hits and 50 Target hits; SELL had 273 Stop hits and 64 Target
hits. The corresponding active-request Stop rates were approximately 84.5%
for BUY and 81.0% for SELL. This is a modest directional difference, not a
strong new asymmetry; IMP-098 likewise found no corrected actionable BUY/SELL
conclusion.

The evidence is consistent with Stop-side exposure being important: the arms
with the narrowest request Stop distances (STOP_ONLY and COMBINED) also had a
one-bar median Stop time and the highest active Stop rates. Because the arms
also have different eligibility populations, this remains an association and
not a causal decomposition.

## Target Analysis

Target was reached 114/685 times (16.6%). Target median holding bars were 6 for
CONTROL, 5 for STOP_ONLY, 10 for TARGET_ONLY, and 6.5 for COMBINED. Target
events therefore generally took longer than Stop events.

The request-level median absolute distances were:

| Arm | Stop distance | Target distance |
|---|---:|---:|
| CONTROL | 0.525 | 3.015 |
| STOP_ONLY | 0.330 | 2.660 |
| TARGET_ONLY | 0.565 | 3.240 |
| COMBINED | 0.315 | 3.025 |

These are request price-unit distances, not evidence of realized movement.
TARGET_ONLY did not convert its larger target-side geometry into robust
realized performance. There were no Timeout outcomes; non-target valid paths
were overwhelmingly Stop outcomes. However, the replay records do not contain
maximum favorable excursion or near-target distance, so unrealized opportunity
cannot be quantified from the finalized replay records.

## Replay Behaviour and Integrity

- 685/685 requests processed.
- Missing mappings: 0; duplicate mappings: 0.
- Closed-M5 chronology: valid.
- Future leakage: not detected.
- Same-bar Stop/Target collisions: 4, all quarantined deterministically.
- Invalid paths: 0.
- Timeouts: 0.
- Two-run replay hash: `541EC9697EAFF3CF4D2723EAD2EFD1598097EACC65E22E418C5AE315B18FAE08`.

Replay quality is therefore supported by the finalized validation evidence.
The negative result is not explained by a replay-integrity failure.

## Arm Comparison

| Arm | Strength | Weakness / observed failure |
|---|---|---|
| CONTROL | Positive point estimate and Profit Factor above 1 on its active sample. | Effective common-support paths only 59; failed bootstrap, temporal, and cost-stress gates. |
| STOP_ONLY | Eligibility improvement and 30 Target hits. | Negative expectancy, 15-loss common-support streak, high Stop frequency, and drawdown above gate. |
| TARGET_ONLY | Closest to break-even; SELL sub-metrics were positive. | BUY was negative, target completion remained low, and stability/effective-sample/cost gates failed. |
| COMBINED | Largest effective common-support count (233). | Worst mean R among arms, 27-loss streak, high Stop frequency, and failed all-arm robustness. |

This comparison does not select a winning arm.

## Evidence, Interpretation, and Unknowns

### Evidence

- IMP-098 measured both wider rejected Stops and shorter available Targets.
- IMP-099 showed all three geometry contrasts improved frozen RR eligibility.
- IMP-100 showed Stop-first outcomes dominate active replay and no arm passed
  realized-outcome gates.
- Replay chronology, collision handling, leakage checks, and reproducibility
  all passed.

### Interpretation

- Entry-time RR eligibility is necessary but insufficient for positive replay
  performance.
- The geometry changes altered which requests became tradable, but did not
  ensure that subsequent price paths reached the Target before the Stop.
- Early Stop clustering is the dominant observed replay pattern; its causal
  attribution remains unresolved.

### Unknowns

- Structure age and move-origin timing are absent from IMP-098 provenance.
- Entry lateness cannot be separated from the RR-coupled span proxy.
- MFE/MAE and near-target distance are not present in replay records.
- Target ladder values are obstruction proxies, not causal identification of
  opposing liquidity.

## Recommended Research Priorities

These are research directions only; none authorizes Runtime or deployment.

1. **Highest value:** add a preregistered Train-only path-diagnostic study for
   MFE/MAE, time-to-adverse-excursion, and distance-to-target before Stop,
   while preserving the same closed-bar causal boundary.
2. **High value:** recover structure age, move-origin, and entry-location
   provenance so late-entry and developed-move hypotheses can be tested rather
   than inferred from an RR-coupled proxy.
3. **Medium value:** test whether Stop clustering persists across independent
   chronological Train blocks and BUY/SELL strata with an explicitly paired
   design; do not introduce a session or time filter from the current evidence.
4. **Required before any qualification:** keep Validation/Test sealed and
   preregister every new hypothesis, population, metric, and stopping rule.

No production change, parameter optimization, Runtime modification, candidate
creation, or deployment is recommended by this review.

## Final Review Status

- Code changed: false.
- Runtime changed: false.
- Protected Modules changed: false.
- Replay rerun: false.
- New experiment executed: false.
- Commit/push: not performed.
