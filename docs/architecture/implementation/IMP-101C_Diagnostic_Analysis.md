# IMP-101C Diagnostic Analysis

Version: 1.0.0

Status: Documentation finalized; Train-only diagnostic analysis complete

Architecture Baseline: ABR-1.0 (Frozen)

Runtime: Unchanged

Protected Modules: Unchanged

Deployment: Not authorized

## Purpose

Finalize the IMP-101C interpretation of the frozen Train-only diagnostic
evidence. This document does not rerun replay, regenerate diagnostics,
recompute statistics, alter earlier IMP-101-series evidence, or authorize a
Runtime, training, Risk, Execution, or deployment change.

The analysis is descriptive and associational. Post-entry observations cannot
establish the cause of an outcome or support a production rule.

## Evidence Boundary

The analytical phase was complete before this documentation sprint. The
following evidence is frozen:

- Dataset records: 685.
- `STOP_FIRST`: 567.
- `TARGET_FIRST`: 114.
- `COLLISION`: 4.
- Duplicate request IDs: 0.
- Missing request IDs: 0.
- Dataset SHA-256:
  `F2D45BAB50AE56933D7634151897A815DCDFD58E1AC48C0AD6F8E08779423E85`.

The three outcome counts sum to all 685 records. The four collisions remain a
distinct ambiguity class and are not interpreted as Stop-first or
Target-first observations.

IMP-101, IMP-101A, and IMP-101B evidence remains unchanged. Replay was not
rerun, and no diagnostic artifact or statistic was regenerated.

## Interpretation Rules

- `SUPPORTED` means the frozen diagnostic result is consistent with the
  preregistered hypothesis at the documented analytical boundary.
- `INCONCLUSIVE` means the available evidence cannot resolve the hypothesis.
  It does not mean the hypothesis is false.
- A supported diagnostic association is not a causal finding.
- Missing or deferred provenance is reported as a limitation, not inferred or
  reconstructed.
- No finding in this document is a production-readiness, strategy, parameter,
  or deployment decision.

## Frozen Hypothesis Results

| ID | Result | Frozen evidence | Bounded interpretation |
| --- | --- | --- | --- |
| H1 | INCONCLUSIVE | Normalized initial MAE was unavailable. | The specified initial adverse-excursion contrast cannot be evaluated. |
| H2 | SUPPORTED | Median time-to-MAE was 1 bar; median time-to-MFE was 6 bars. | The documented adverse extreme occurred earlier by the median summaries. |
| H3 | SUPPORTED | Median Target-first `MFE_R` was 6.664; Stop-first was 1.181. | The frozen outcome groups show descriptive normalized-MFE separation. |
| H4 | INCONCLUSIVE | No `ADVERSE_THEN_RECOVERY` observations were present. | The required recovery-category contrast cannot be resolved. |
| H5 | INCONCLUSIVE | Entry-location provenance is `DEFERRED_PROVENANCE`. | No entry-location conclusion is supported. |
| H6 | INCONCLUSIVE | Structure-age and move-origin provenance are deferred. | No age or origin conclusion is supported. |
| H7 | INCONCLUSIVE | Directional effect was not stable across blocks. | The relationship did not meet the required stability condition. |

## Diagnostic Findings

### Timing

H2 is supported at the frozen diagnostic boundary. The median time-to-MAE was
1 bar, while the median time-to-MFE was 6 bars. This is evidence of a timing
difference in the analyzed observations. It does not establish why the
difference occurred, whether it would recur outside this dataset, or whether
an entry or lifecycle rule should change.

### Favorable Excursion

H3 is supported at the frozen diagnostic boundary. Median `MFE_R` was 6.664
for Target-first observations and 1.181 for Stop-first observations. This is a
descriptive outcome-group contrast. Because outcome class and post-entry
excursion are measured on the realized path, the contrast must not be treated
as a pre-entry predictor or causal mechanism.

### Unresolved Questions

H1 is inconclusive because normalized initial MAE is unavailable. H4 is
inconclusive because the required `ADVERSE_THEN_RECOVERY` category has no
observations. H5 and H6 are inconclusive because their required provenance is
deferred. H7 is inconclusive because the directional effect did not remain
stable across chronological blocks.

No value is imputed for unavailable diagnostics, no empty category is treated
as evidence of absence in the underlying process, and no unstable subgroup
effect is promoted to a general conclusion.

## Limitations

- The evidence is limited to the frozen 685-record dataset.
- The analysis is diagnostic and post-entry; it does not identify a causal
  mechanism.
- Normalized initial MAE is unavailable.
- The absence of `ADVERSE_THEN_RECOVERY` observations prevents the H4
  comparison.
- Entry-location, structure-age, and move-origin provenance is deferred.
- Directional behavior does not replicate consistently across chronological
  blocks.
- Four same-bar collisions remain quarantined as ambiguous outcomes.
- The supplied frozen results do not support extrapolation to Validation,
  Test, live, or production populations.
- No production-readiness assessment was performed or authorized.

## Architecture and Governance Compliance

The canonical flow remains:

`Market -> Brain -> AI Runtime -> Decision -> Risk -> Execution -> Trade Lifecycle`

This documentation does not change module boundaries, public contracts,
feature definitions, labels, confidence, Risk authority, Execution authority,
training logic, or live inference. Brain remains market-understanding only,
Risk remains the final permission gate, and Execution receives only
risk-approved decisions.

## Final Conclusion

H2 and H3 are supported as bounded diagnostic findings. H1, H4, H5, H6, and
H7 are inconclusive for their stated evidence limitations. These results do
not establish causality, justify a trading-system modification, demonstrate
production readiness, or authorize deployment.

IMP-101C documentation finalization leaves Runtime and Protected Modules
unchanged. Further action requires separate review and authorization.
