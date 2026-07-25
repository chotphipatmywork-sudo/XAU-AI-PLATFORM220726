# IMP-079 Offline Structural Opportunity Research

Version: 1.1.0

Date: 2026-07-22

Status: Completed; structural target bottleneck confirmed; NO-GO

Architecture Baseline: ABR-1.0

Related: CR-013, CR-015, CR-016, CR-017, IMP-073, IMP-075, IMP-078

## Purpose

Replace serial Runtime candidate changes with a Train-only structural
opportunity diagnostic. CR-016 and CR-017 both failed their smoke gates before
Risk because the surviving Entry/Stop/Target geometry could not satisfy the
unchanged cost-aware minimum `2.0R`. The next step is therefore evidence
collection and diagnosis, not another Runtime strategy contract.

## Frozen sources and boundary

The diagnostic may use only:

- CR-015 quality-audited pre-Train Objective Setup/Decision artifacts;
- the Objective minimum-reclaim Setup/Decision source only for observations
  strictly before frozen Validation start `2025-07-16 03:00`;
- the frozen augmented Train outcome file with SHA-256
  `F31E6DED4E0AC3B20FDD7964D3E634902736C8AD3316AA15A4E63D5C3C7E9A7E`;
- the two approved real-tick quality-exclusion manifests.

The tool must verify frozen hashes, stop at the Train cutoff, and report
`validation_dataset_used=false` and `test_dataset_used=false`. Validation/Test
partition files are forbidden inputs.

## Frozen questions

For every quality-admissible sweep/reclaim trigger, measure:

- accepted plan, below-minimum-RR, invalid-geometry, and other fail-closed
  disposition;
- calculable cost-aware RR distribution and the share below `1R`, below `2R`,
  and at least `2R`;
- additional structural Target-distance multiplier required to reach `2R`
  where V1 audit values are calculable;
- coverage by BUY/SELL, Session Progress bucket, source period, and four
  chronological blocks;
- the cost-aware outcome baseline of the frozen augmented Train plans.

This stage is descriptive. It may not tune a threshold, change Target source,
train a model, rank with Validation/Test, or authorize a Runtime candidate.

## Fail-closed limitations

Setup Audit V1 does not preserve trigger Entry for invalid-geometry rows and
does not preserve a ladder of alternative confirmed structural Targets.
Rejected triggers also have no counterfactual outcome. The diagnostic must
state these limitations and must not invent missing prices or labels.

If the evidence confirms insufficient target room, the next artifact is a
past-only multi-level structural-target exporter/replay for Train research.
Only after alternatives are measured and one candidate passes the existing
Train-only stability gates may a new Runtime Change Request be proposed.

## Protected boundaries

- no MQL5 Runtime, Brain, Decision, Risk, Execution, or lifecycle change;
- canonical Feature Schema 4.0 and Label Schema 1.1 remain unchanged;
- minimum `2.0R`, structural Stop, and Safety Locks remain unchanged;
- no Forward, Deployment, broker mutation, or live execution;
- status remains `OBJECTIVE_STRUCTURAL_PLAN_RESEARCH_NO_GO`.

## Validation

Add a focused synthetic Python test for cutoff enforcement, quality exclusion,
disposition accounting, RR/shortfall metrics, and fail-closed schema checks.
Then run the complete Python regression. No MetaEditor target is affected
because this implementation may not modify MQL5 source.

## Train-only result

All eight frozen source hashes passed. The main source reader stopped at the
frozen Train end `2025-07-16 03:00`; both Validation and Test usage flags
remained false. After observation-date quality quarantine, the combined
pre-Train and Train evidence contained 1,777 sweep/reclaim triggers:

```text
accepted structural plans       234  (13.17%)
below minimum RR              1,449
invalid structural geometry      38
other fail-closed                 56
```

Of 1,683 triggers with calculable V1 plan geometry, median cost-aware RR was
`0.883R`, the 25th/75th percentiles were `0.487R`/`1.495R`, 926 were below
`1R`, 525 were from `1R` to below `2R`, and only 232 reached at least `2R`
without floating-point tolerance. For the 1,449 below-minimum plans, the
median required Target-distance multiplier was `2.33x` and the median
shortfall was 182 points.

The bottleneck was not isolated to one side or one period. Plan reachability
was `12.39%` for BUY and `14.16%` for SELL. Across four chronological trigger
blocks it was `13.06%`, `10.59%`, `10.36%`, and `18.65%`; structural failure
remained above `81%` in every block. Early Session had somewhat better
reachability (`15.57%`) than late Session (`10.67%`), but this descriptive
stage does not authorize a Session filter.

The frozen augmented Train baseline contained 233 mature plans, 59 Target-first
and 174 Stop-first, for target rate `25.32%` and mean cost-aware return
`-0.078R`. Therefore the current contract has both a broad structural-room
constraint and negative accepted-plan expectancy.

## Conclusion and next evidence

No Runtime candidate is ready. The existing V1 artifact cannot rank Target
alternatives because it preserves neither the trigger Entry for
invalid-geometry rows nor a past-only ladder of confirmed Target levels. The
next bounded research artifact is a past-only multi-level structural-target
exporter or replay. It must compare alternatives on Train only before any new
Runtime Change Request is proposed. Minimum `2.0R`, Risk, Validation/Test
seals, Forward, and Deployment remain unchanged.

The focused synthetic test and complete Python regression passed 45/45. No
MQL5 file changed in IMP-079, so no MetaEditor target required recompilation.
The ignored result is retained at
`training/output/structural_opportunity_train_only_202001_202507/structural_opportunity_diagnostic.json`.
