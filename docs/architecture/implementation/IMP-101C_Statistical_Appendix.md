# IMP-101C Statistical Appendix

Version: 1.0.0

Status: Documentation finalized; frozen statistics recorded

Architecture Baseline: ABR-1.0 (Frozen)

Runtime: Unchanged

Protected Modules: Unchanged

Deployment: Not authorized

## Purpose

Record the frozen IMP-101C dataset-integrity and hypothesis statistics without
rerunning replay, regenerating diagnostics, recomputing values, or changing
IMP-101, IMP-101A, or IMP-101B evidence.

This appendix reports only supplied, verified values. It does not introduce
new statistical tests, causal estimates, confidence claims, production gates,
or trading recommendations.

## Dataset Integrity

| Check | Frozen result |
| --- | ---: |
| Total records | 685 |
| `STOP_FIRST` | 567 |
| `TARGET_FIRST` | 114 |
| `COLLISION` | 4 |
| Duplicate request IDs | 0 |
| Missing request IDs | 0 |

Outcome-count reconciliation:

`567 + 114 + 4 = 685`

Dataset SHA-256:

`F2D45BAB50AE56933D7634151897A815DCDFD58E1AC48C0AD6F8E08779423E85`

The hash identifies the frozen dataset used by the completed analytical phase.
It is recorded for traceability and was not regenerated in this sprint.

## Frozen Descriptive Statistics

| Statistic | Frozen value | Unit |
| --- | ---: | --- |
| Median time-to-MAE | 1 | M5 bar |
| Median time-to-MFE | 6 | M5 bars |
| Median Target-first `MFE_R` | 6.664 | R |
| Median Stop-first `MFE_R` | 1.181 | R |

These medians describe the frozen observations. They do not by themselves
measure causality, out-of-sample stability, economic value, or production
fitness.

## Hypothesis Disposition

| ID | Disposition | Statistical or evidence basis |
| --- | --- | --- |
| H1 | INCONCLUSIVE | Normalized initial MAE unavailable; the required comparison cannot be calculated from the frozen evidence. |
| H2 | SUPPORTED | Frozen medians: time-to-MAE 1 bar and time-to-MFE 6 bars. |
| H3 | SUPPORTED | Frozen medians: Target-first `MFE_R` 6.664 and Stop-first `MFE_R` 1.181. |
| H4 | INCONCLUSIVE | Zero `ADVERSE_THEN_RECOVERY` observations; the required category contrast is unavailable. |
| H5 | INCONCLUSIVE | Entry-location data remains `DEFERRED_PROVENANCE`. |
| H6 | INCONCLUSIVE | Structure-age and move-origin data remain `DEFERRED_PROVENANCE`. |
| H7 | INCONCLUSIVE | Directional effect is not stable across chronological blocks. |

`SUPPORTED` is limited to consistency with the frozen diagnostic result.
`INCONCLUSIVE` identifies insufficient, unavailable, or unstable evidence and
is not evidence that the hypothesis is false.

## Availability and Missing-Evidence Matrix

| Evidence item | Availability | Consequence |
| --- | --- | --- |
| Outcome identity | Complete | All 685 records reconcile to a frozen outcome class. |
| Request identity | Complete | Zero duplicate and zero missing request IDs were reported. |
| Normalized initial MAE | Unavailable | H1 remains inconclusive. |
| Time-to-MAE and time-to-MFE medians | Available | Supports the bounded H2 timing interpretation. |
| Outcome-group `MFE_R` medians | Available | Supports the bounded H3 descriptive contrast. |
| `ADVERSE_THEN_RECOVERY` category | Zero observations | H4 remains inconclusive. |
| Entry-location provenance | `DEFERRED_PROVENANCE` | H5 remains inconclusive. |
| Structure-age and move-origin provenance | `DEFERRED_PROVENANCE` | H6 remains inconclusive. |
| Chronological directional stability | Not stable | H7 remains inconclusive. |

## Interpretation Constraints

- No unreported distribution, interval, effect size, significance level, or
  model result is inferred.
- The difference between displayed medians is not presented as a new computed
  statistic or as a causal effect.
- Outcome-conditioned `MFE_R` summaries are post-entry descriptions and are
  not pre-entry predictors.
- An empty observed path-shape category does not prove that the path shape is
  impossible outside this dataset.
- Deferred provenance is not substituted with a proxy.
- Chronological instability prevents a stable directional conclusion.
- Collision records remain distinct and are not reassigned.

## Limitations

- Only the frozen summary statistics supplied for IMP-101C are recorded.
- Normalized initial MAE is unavailable.
- No `ADVERSE_THEN_RECOVERY` observations are available for comparison.
- Required provenance for H5 and H6 is deferred.
- H7 lacks chronological stability.
- No additional uncertainty estimates are introduced in this finalization
  sprint.
- The evidence does not establish external validity, causality, profitability,
  or production readiness.

## Reproducibility and Scope Record

- Analytical phase: complete before documentation finalization.
- Dataset records: 685.
- Duplicate request IDs: 0.
- Missing request IDs: 0.
- Replay: not rerun.
- Diagnostics: not regenerated.
- Statistics: not recomputed.
- Runtime: unchanged.
- Protected Modules: unchanged.
- Training logic: unchanged.
- Deployment: not authorized.

This appendix is a traceability record for the frozen analysis. It authorizes
no implementation, candidate selection, commit, push, or deployment action.
