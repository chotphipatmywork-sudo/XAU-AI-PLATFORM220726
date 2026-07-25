# XAU AI External Training Pipeline

This folder is offline-only. It does not run inside MetaTrader 5 and does not place trades.

Use only CSV partitions regenerated with Feature Schema `4.0.0` and the Label Schema `1.1.0` 16-bar temporal purge. It exposes three Trend components, two Volatility components, three Liquidity components, three one-hot Session fields, and Session Progress while preserving the four canonical feature groups. Schema 3.0 CSV partitions and all earlier model artifacts are incompatible.

## Stage D Setup Outcome research

CR-013 Stage D uses a separate Setup Outcome Schema `1.0.0`; it does not alter
the directional Label Schema `1.1.0`. Build it only from isolated Objective
Strategy Tester Setup and Decision audits:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\build_stage_d_setup_outcomes.ps1
```

The registered five-year XAUUSD evidence must also pass its versioned MT5 tick
quality exclusions:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\build_stage_d_setup_outcomes.ps1 `
  -OutputName stage_d_setup_quality_real_ticks_202107_202606 `
  -QualityExclusions training\config\stage_d_real_tick_quality_exclusions_202107_202606.json
```

The builder follows at most 64 later completed M15 bars and records
`TARGET_FIRST`, `STOP_FIRST`, or `TIMEOUT`. Same-bar Target/Stop observations
are quarantined as `AMBIGUOUS`; incomplete paths are `UNMATURED`. Model features
are exactly the existing twelve Feature Schema 4.0 values. Plan prices, RR,
MFE/MAE, outcome, Risk, and Execution fields are audit-only and forbidden from
the model matrix.

CR-016 Setup Audit Schema 2.0 adds the exact confirmation-bar open,
continuation-confirmed flag, and confirmation extension. The Dataset builder
continues to accept preserved Schema 1.0 artifacts, but a Schema 2.0 plan is
rejected unless both its sweep/reclaim trigger and continuation confirmation
are true. This compatibility does not mix candidate evidence; comparisons must
retain their source contract identity.

The frozen CR-016 candidate was rejected at its 2021-06 real-tick smoke gate:
1,911 observations produced 121 confirmed POIs, 28 triggers, 12 continuation
confirmations, and zero valid structural plans. The builder must continue to
fail closed for that artifact; it must not be made trainable by reducing the
minimum RR, changing structural Targets, or bypassing Risk.

CR-017 Setup Audit Schema 3.0 replaces the rejected candidate fields with
`context_bar_open`, `reversal_context_confirmed`, and
`trigger_engulfment_atr`. The latest completed M5 bar is again the Entry
trigger and the prior completed M5 bar is causal context. The Dataset builder
preserves exact V1/V2 compatibility and refuses any V3 plan that bypasses the
trigger or reversal-context evidence.

The frozen CR-017 2021-06 real-tick smoke artifact contains 1,911 observations,
103 confirmed POIs, 11 triggers, three reversal confirmations, and zero valid
plans. All three plan RR values were below `0.80R`, so the V3 artifact must
remain non-trainable and the candidate is retired without relaxing `2.0R`.

`diagnose_structural_opportunity.py` replaces serial Runtime trials with a
hash-frozen Train-only geometry audit. It combines quality-admissible CR-015
pre-Train evidence and the main Objective source only before the frozen
Validation cutoff, then reports trigger disposition, RR/Target shortfall,
direction, Session bucket, chronological blocks, and the augmented Train
outcome baseline. It cannot read Validation/Test partitions, train, modify
Runtime, or authorize Deployment. The current result found 1,777 triggers but
only 234 accepted plans; median calculable RR was `0.883R`, while the accepted
233-plan Train baseline retained mean return `-0.078R`. A past-only multi-level
Target artifact is required before another Runtime Change Request.

The canonical join time is the completed M15 boundary. With real ticks, the
actual Decision `recorded_at` may follow that boundary by zero to 120 seconds
while waiting for the first tick. Early timestamps and lags above the frozen
Runtime freshness limit are rejected.

The tool refuses to split unless there are at least 200 mature, non-ambiguous
plans, including at least 40 Target and 40 non-Target rows. The chronological
split removes every row whose outcome was not known before the next partition
began. Validation and Test remain sealed.

Only after the split reports `ready_for_train_only_ranking: true`, run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\run_stage_d_setup_quality_research.ps1
```

The ranker accepts only the Train partition and uses four expanding folds with
outcome-known-time purging. Every artifact remains `SETUP_QUALITY_RESEARCH_NO_GO`;
no Stage D script can integrate MQL5 Runtime or authorize deployment.

The registered five-year Train-only run failed its stable four-fold gate. It
wrote diagnostics only; no preliminary model exists and Validation/Test remain
sealed.

CR-015 may prepend quality-controlled outcomes strictly earlier than the frozen
Train boundary with `augment_pretrain_history.py`. The tool verifies the frozen
Train/Validation/Test SHA-256 values, parses only Train sources, and treats
Validation/Test as opaque hash inputs. The 200/40/40 readiness gate remains
unchanged; passing readiness permits only the existing Train-only purged
walk-forward ranker and does not authorize deployment.

CR-014 Stage 1 can inspect preregistered Setup V2 associations without fitting
a model or accepting Validation/Test paths:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\run_setup_v2_hypothesis_diagnostic.ps1
```

The registered run found no stable preregistered Trend/Liquidity promotion.
Early and late Session progress were stable exploratory associations only; they
must be confirmed on a new untouched later period and cannot authorize Stage 2,
Runtime, deployment, or trading.

IMP-072 freezes that later-period confirmation before new evidence is opened.
The confirmation Dataset must be generated from Objective M15/M5 `Every tick
based on real ticks` evidence beginning strictly after `2026.06.26 21:30`.
After the new Strategy Tester run, build the separately named Dataset with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\build_setup_v2_session_confirmation.ps1
```

Do not run the one-shot confirmation until the build summary shows at least 80
mature plans, 15 Target plans, and 40 non-Target plans. Then run exactly once:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\run_setup_v2_session_confirmation.ps1
```

The tool rejects old evidence and files named Train, Validation, or Test. A
pass can only request Stage 2 review; all deployment locks remain false.

## Objective Setup failure diagnostic

The frozen Stage D Train and Setup Audit can be inspected for observation-time
geometry failure modes without opening Validation/Test or fitting a model:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\run_objective_setup_failure_diagnostic.ps1
```

The registered run found one stable candidate: completed M5 reclaim distance
of at least 0.10 ATR. It improved both Target rate and cost-aware expectancy in
all four purged folds. The owner approved that threshold for the Objective
Setup contract on 2026-07-19. All earlier datasets remain diagnostic evidence;
new real-tick evidence must be generated before evaluating the amended setup.
Runtime deployment and Forward trading remain prohibited.

The amended five-year real-tick build produced 260 trainable outcomes but only
182 chronological Train rows, below the frozen 200-row ranking minimum. The
tool therefore stopped before Train-only ranking. Train Target rate and mean
cost-aware return improved descriptively, but mean return remained negative.
Do not lower the sample gate, alter the split, or use Validation/Test to force
this contract through.

## One-command Objective research finalization

After an Objective real-tick Strategy Tester run finishes, archive and process
the complete evidence with one command:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\finalize_objective_research_run.ps1 `
  -OutputName <unique_evidence_name>
```

The finalizer records SHA-256 hashes, refuses uncovered MT5 real-tick warning
dates, builds from archived artifacts, creates the temporal split, performs a
Train-only descriptive comparison, and runs the fixed residual diagnostic.
It never uses Validation/Test for selection and cannot authorize deployment.

The registered same-month comparison with `1 minute OHLC` failed exact
Setup/Plan parity. Stage D generation must therefore use `Every tick based on
real ticks`. The retained diagnostic comparison can be reproduced with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\compare_stage_d_generation_parity.ps1
```

The comparison requires exact Objective Setup/Plan and Feature Schema 4.0
parity. It ignores Risk and paper lifecycle differences. Its current failure
must not be weakened; final strategy evidence also uses real ticks.

## Current-feed Setup funnel

After a broker-feed parity failure, the complete current `XAUUSD` real-tick
evidence is kept separate from all preserved feed artifacts. Its Setup Audit is
hash-locked and the preregistered current-feed Train-only funnel can be run
with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\diagnose_current_feed_setup_funnel.ps1
```

The diagnostic stops before `2024-07-01 00:00`, never accepts Validation/Test
paths, and cannot train, modify Runtime/Risk, relax `2.0R`, or authorize
deployment.

The corresponding outcome-blind current-feed Target-ladder request can be
prepared with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\prepare_current_feed_target_research.ps1
```

It includes only reversal-confirmed contexts before the same Train cutoff and
retains the frozen `2.0R` contract.

After the strict Target replay, current-feed Entry/Stop path behavior can be
measured without selecting a candidate:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\diagnose_current_feed_entry_stop.ps1
```

The preregistered current-feed M5 lifecycle request can then be prepared with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\prepare_current_feed_lifecycle_research.ps1
```

## What it trains

`train_classifier.py` trains a class-balanced logistic-regression baseline from the time-ordered CSV partitions. It selects one of three regularization strengths using Validation macro F1, then evaluates the selected model once on Test data.

The baseline writes:

- `xau_ai_classifier.joblib` — Python-only model artifact.
- `xau_ai_classifier_metadata.json` — contract versions, metrics, and eligibility result.

The joblib artifact is not loadable by MQL5. ONNX export and an MQL5 inference adapter are separate future tasks.

## Install Python dependencies

Install Python 3.11 or later from [python.org](https://www.python.org/downloads/). In PowerShell, from this `training` directory:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Train

The three CSV files are created by MetaTrader under its `MQL5\Files` folder. In MT5, use **File → Open Data Folder**, then open `MQL5\Files` and copy the three files to a convenient location.

Run this command, replacing the example paths with your copied CSV location:

```powershell
.\.venv\Scripts\python.exe train_classifier.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --validation "C:\dataset\XAU_AI_TRAINING_VALIDATION.csv" `
  --test "C:\dataset\XAU_AI_TRAINING_TEST.csv" `
  --output-dir ".\output"
```

Read `output\xau_ai_classifier_metadata.json`. Only a result with `eligible_for_shadow_deployment: true` meets the current baseline evaluation gate. This still does not authorize live trading.

## Candidate diagnostics without reusing Test

The first baseline has already been evaluated on the current Test partition. Do not run more candidate-selection experiments against that Test file. Use this command to compare candidate models with Train and Validation only:

```powershell
.\.venv\Scripts\python.exe select_candidate.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --validation "C:\dataset\XAU_AI_TRAINING_VALIDATION.csv" `
  --output-dir ".\output"
```

Read `output\candidate_diagnostics.json` and share it for review. The selected artifact is preliminary only. After selecting a candidate, create a new untouched later-period Test dataset before final evaluation.

## Probability decision policy

Candidate selection evaluates the model's SELL/HOLD/BUY probabilities with ordinary `argmax`, confidence floors, and margin-only policies. A confidence policy emits BUY or SELL only when its probability and directional margin meet the selected thresholds; otherwise it emits HOLD. Lower floors and margin-only variants preserve useful relative rankings from class-balanced models. This can improve directional precision without adding a fifth feature or using Test during selection.

The selected preliminary model has a paired `output\xau_ai_candidate_preliminary_policy.json` file. It is Validation-only metadata, not an MQL5 deployment artifact. Verify the policy implementation with:

```powershell
.\.venv\Scripts\python.exe test_probability_decision_policy.py
```

## Read-only feature diagnostic

This diagnostic reads the selected preliminary model plus Train and Validation only. It writes a JSON report but does not train a model, change the CSV files, or read Test data.

```powershell
.\.venv\Scripts\python.exe diagnose_features.py `
  --model ".\output\xau_ai_candidate_preliminary.joblib" `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --validation "C:\dataset\XAU_AI_TRAINING_VALIDATION.csv" `
  --output ".\output\feature_diagnostic.json"
```

Read `output\feature_diagnostic.json`. Features with a near-zero validation permutation macro-F1 drop are weak candidates for further Brain investigation; this result alone does not authorize changing the canonical four-feature contract.

## Walk-forward selection inside Train

After the Validation-only experiments are reviewed, use walk-forward selection to avoid continuing to tune against the same Validation period. This script accepts only Train, creates four expanding chronological folds internally, purges the approved 16-bar label horizon before every evaluation and calibration boundary, compares raw and chronologically calibrated probabilities, and locks one development candidate:

```powershell
.\.venv\Scripts\python.exe walk_forward_select.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output-dir ".\output"
```

First run `test_walk_forward_training.py`. `--purge-bars` defaults to and is contractually fixed at `16`. The resulting locked joblib and policy JSON are development artifacts only. Do not read the existing Test partition or deploy the artifact to MQL5. Generate a newly dated evaluation period after the method is frozen.

## Train-only walk-forward feature diagnostic

When the Train-only walk-forward candidate fails the stable gate, diagnose the selected method without reading Validation or Test:

```powershell
.\.venv\Scripts\python.exe test_walk_forward_feature_diagnostic.py
.\.venv\Scripts\python.exe walk_forward_feature_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --selection-report ".\output\walk_forward_diagnostics.json" `
  --output ".\output\walk_forward_feature_diagnostic.json"
```

The report ranks the continuous Feature Contract 3.0 dimensions plus the complete Session one-hot group by their fold-aggregated Macro F1 and BUY-precision drops. The three Session columns are permuted together to preserve valid categorical rows. Negative or inconsistent drops mean that permuting the feature sometimes improved the metric; do not interpret importance as causal trading value.

## Nested purged walk-forward estimate

After the ordinary purged walk-forward method and candidate grid are frozen, estimate the complete selection process with separate Inner and Outer folds:

```powershell
.\.venv\Scripts\python.exe test_nested_walk_forward_training.py
.\.venv\Scripts\python.exe nested_walk_forward_select.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output-dir ".\output"
```

The default method uses four Outer folds, three Inner folds, and a contract-fixed 16-bar purge. Inner folds select model, probability variant, and an asymmetric SELL/BUY confidence policy. Outer folds alone estimate the selected process. The script does not accept Validation or Test paths, and its locked artifacts are not deployable in MQL5.

## Temporal regime drift diagnostic

When the nested Outer estimate is unstable, reproduce its selected folds and inspect distribution shift without reselecting a model:

```powershell
.\.venv\Scripts\python.exe test_temporal_regime_diagnostic.py
.\.venv\Scripts\python.exe temporal_regime_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --nested-report ".\output\nested_walk_forward_diagnostics.json" `
  --output ".\output\temporal_regime_diagnostic.json"
```

The report measures standardized feature shifts, label and prediction distributions, and results by Session and numeric Trend/Volatility/Liquidity regimes. Calibrated folds also receive a raw-probability counterfactual using the same model and policy. These are diagnostic associations only; they do not authorize changing the feature contract or deploying a model.

## Controlled history strategy comparison

Test whether older temporal regimes are degrading a fixed model by changing only its history strategy:

```powershell
.\.venv\Scripts\python.exe test_history_strategy_diagnostic.py
.\.venv\Scripts\python.exe history_strategy_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\history_strategy_diagnostic.json"
```

The fixed raw depth-5 balanced forest with argmax is evaluated using expanding history, rolling windows, and exponential recency weights over the same purged Train-only folds. The comparison is diagnostic because those Train periods have already been inspected; a winning strategy is not deployment evidence.

## Feature-label stability diagnostic

Measure whether fixed feature regimes retain the same future-label relationship across the non-overlapping Train Outer periods:

```powershell
.\.venv\Scripts\python.exe test_feature_label_stability_diagnostic.py
.\.venv\Scripts\python.exe feature_label_stability_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --nested-report ".\output\nested_walk_forward_diagnostics.json" `
  --output ".\output\feature_label_stability_diagnostic.json"
```

The report uses fixed buckets, SELL/HOLD/BUY rates, Jensen-Shannon divergence, and ordered high-minus-low BUY spreads. It does not fit a model. Direction reversals are evidence of association drift only and must not be converted directly into live trading rules.

## Derived Trend interaction diagnostic

Compare deterministic interactions from the existing Trend Regime, Momentum, and Slope values without changing MQL5 or the active feature contract:

```powershell
.\.venv\Scripts\python.exe test_trend_interaction_diagnostic.py
.\.venv\Scripts\python.exe trend_interaction_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\trend_interaction_diagnostic.json"
```

The comparison appends bounded extension, agreement, and lead candidates to one fixed raw depth-5 model over the same purged Train Outer periods. Derived columns remain diagnostic-only until a separate nested comparison demonstrates temporal consistency and a Feature Contract change is explicitly approved.

Run the bounded nested Baseline-vs-Agreements confirmation with:

```powershell
.\.venv\Scripts\python.exe test_nested_trend_agreement_diagnostic.py
.\.venv\Scripts\python.exe nested_trend_agreement_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\nested_trend_agreement_diagnostic.json"
```

The fixed model and policy prevent feature selection from being confused with model or threshold search. A full-Train Inner preference is insufficient when the feature set is not selected consistently before unseen Outer periods.

## Past-only Trend dynamics diagnostic

After static Trend agreements were rejected, compare bounded changes derived only from the current and earlier replay rows:

```powershell
.\.venv\Scripts\python.exe test_trend_dynamics_diagnostic.py
.\.venv\Scripts\python.exe trend_dynamics_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\trend_dynamics_diagnostic.json"
```

The diagnostic compares recent Regime, Momentum, and Slope deltas plus Regime age with the unchanged Schema 3.0 Baseline. These derived columns are offline-only and cannot be added to MQL5 from a controlled comparison alone.

Confirm the winning seven-column Trend-change set with bounded Inner selection before unseen Outer periods:

```powershell
.\.venv\Scripts\python.exe test_nested_trend_dynamics_diagnostic.py
.\.venv\Scripts\python.exe nested_trend_dynamics_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\nested_trend_dynamics_diagnostic.json"
```

This comparison uses four Outer folds, three Inner folds, fixed raw depth-5 balanced forests, argmax, and 16-record purges. It does not accept Validation or Test paths. In the recorded experiment, Inner selection preferred Trend Changes in only one of four Outer histories and no Outer fold passed the complete gate; Feature Schema 3.0 therefore remained unchanged.

## Feature sufficiency and label ambiguity

Measure whether similar Schema 3.0 rows have consistent future labels before adding more model complexity:

```powershell
.\.venv\Scripts\python.exe test_feature_sufficiency_diagnostic.py
.\.venv\Scripts\python.exe feature_sufficiency_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\feature_sufficiency_diagnostic.json"
```

The default diagnostic standardizes features inside each past training fold, finds 25 nearest past rows, and measures true-label support, label entropy, nearest-label agreement, and local-majority metrics. It compares the full schema with canonical feature-group views but does not select a feature contract or model. Use `--neighbours 15` and `--neighbours 50` only as sensitivity checks; Validation and Test remain excluded.

## Confidence-versus-coverage diagnostic

Before tuning another abstention policy, measure whether the fixed raw model has a stable high-confidence directional region:

```powershell
.\.venv\Scripts\python.exe test_confidence_coverage_diagnostic.py
.\.venv\Scripts\python.exe confidence_coverage_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\confidence_coverage_diagnostic.json"
```

The diagnostic uses the fixed raw depth-5 balanced forest over four purged Train folds and reports a predefined symmetric confidence grid. It does not select or lock a policy. A threshold is not credible unless both SELL and BUY have at least 25 predictions and at least 0.50 precision in every fold. The recorded experiment found no stable threshold, so further confidence-policy tuning was stopped.

## Liquidity temporal context research

CR-003 evaluates bounded past-only Liquidity changes and sweep memory without changing Schema 4.0:

```powershell
.\.venv\Scripts\python.exe test_liquidity_temporal_diagnostic.py
.\.venv\Scripts\python.exe liquidity_temporal_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\expanded_20260716\liquidity_temporal_diagnostic.json"
```

The controlled report itself decides whether nested confirmation is authorized using the predeclared CR-003 promotion boundary. Validation and Test are never accepted as inputs.

## Temporal Brain feature window research

CR-004 compares the current canonical Brain row with fixed past-row windows:

```powershell
.\.venv\Scripts\python.exe test_temporal_feature_window_diagnostic.py
.\.venv\Scripts\python.exe temporal_feature_window_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\expanded_20260716\temporal_feature_window_diagnostic.json"
```

The experiment appends exact prior Schema 4.0 rows at lags 1, 4, and 8. It is research-only and cannot authorize a sequence-input Runtime contract.

## Historical Session progress context evidence

The following commands produced the pre-implementation Schema 3.0 evidence for CR-001. Do not run them against Schema 4.0 partitions because Session Progress is now already present in the canonical tensor:

```powershell
.\.venv\Scripts\python.exe test_session_context_diagnostic.py
.\.venv\Scripts\python.exe session_context_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\session_context_diagnostic.json"
```

`session_progress` maps elapsed minutes inside the current eight-hour Asia, London, or New York block to `0..100`. CR-001 has now approved and implemented this field as the twelfth Schema 4.0 feature.

Confirm it with Inner selection before unseen Outer periods:

```powershell
.\.venv\Scripts\python.exe test_nested_session_context_diagnostic.py
.\.venv\Scripts\python.exe nested_session_context_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\nested_session_context_diagnostic.json"
```

The recorded nested experiment selected Session Progress in three of four Outer histories and supported CR-001 architecture review. It did not pass the deployment gate; the implemented Schema 4.0 dataset must be regenerated and evaluated independently.

Verify the active strict Python schema with:

```powershell
.\.venv\Scripts\python.exe test_feature_schema_contract.py
```

## Schema 4.0 Session Progress ablation

After regenerating and validating Schema 4.0, isolate the new final field from the
three existing Session one-hot values with a Train-only nested comparison:

```powershell
.\.venv\Scripts\python.exe test_schema4_session_progress_ablation.py
.\.venv\Scripts\python.exe schema4_session_progress_ablation.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --output ".\output\schema4_session_progress_ablation.json"
```

The model and argmax policy are fixed, Inner folds select with or without Session
Progress, every boundary purges 16 records, and Validation/Test are not read.

## Closed-H1 context research

After `TestHistoricalH1ContextExporter` creates
`XAU_AI_H1_CONTEXT_RESEARCH.csv`, run the strict Train-only controlled comparison:

```powershell
.\.venv\Scripts\python.exe test_h1_context_diagnostic.py
.\.venv\Scripts\python.exe h1_context_diagnostic.py `
  --train "C:\dataset\XAU_AI_TRAINING_TRAIN.csv" `
  --h1-context "C:\dataset\XAU_AI_H1_CONTEXT_RESEARCH.csv" `
  --output ".\output\h1_context_diagnostic.json"
```

The research file is joined by Dataset ID and Timestamp. It does not change the
active Feature Schema and cannot authorize deployment.

## Past-only structural Target replay

IMP-080 replaces serial Runtime CR trials with an isolated Train-only Target
ladder export. Prepare the frozen 1,777-request artifact and copy it to the MT5
Files sandbox with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\prepare_past_only_target_research.ps1
```

Compile the focused exporter with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\compile_past_only_target_research.ps1
```

Before the first historical collection, set MT5 `Tools > Options > Charts >
Max bars in chart` to `Unlimited` and restart MT5. The exporter prefetches the
required M5/M15 windows from local annual history and reports the current
Terminal Max Bars value if history remains unavailable.

Attach `TestPastOnlyStructuralTargetExporter` once to an XAUUSD chart. It has
no order calls, writes `XAU_AI_PAST_ONLY_TARGET_LADDERS.csv`, reports
`deployment=false`, and removes itself. Then collect and run the sealed replay:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\collect_past_only_target_research.ps1
```

The replay uses only observations and mature outcomes before the frozen Train
cutoff. Validation/Test, Runtime, Risk, Forward, and Deployment remain sealed.

The completed 1,777-request replay rejected all seven Target-only candidates.
The current Target reproduced the frozen `-0.078R` baseline; every alternative
with at least 200 mature records also had negative mean cost-aware R. See
`IMP-080_Past_Only_Multilevel_Structural_Target_Replay.md` before proposing
further Entry/Stop research.

## Research Scorecard Standard 1.0

Generate the current frozen Baseline scorecard with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\build_research_scorecard.ps1
```

For a later Candidate, pass `-MetricsPath`, `-ScorecardPath`, and optionally
`-ReferencePath` pointing to the accepted Baseline scorecard. The calculator
reports Research Quality, Strategy Evidence, Operational Safety, weighted
Overall Readiness, component deltas, G0-G8, and the final NO-GO/review status.
Unknown evidence receives no invented credit and a failed Train gate caps the
overall score at 49 regardless of Engineering quality.

## Effective Setup Sample audit

Audit the frozen IMP-080/CR-015 Train baseline for duplicate and overlapping
outcome windows with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\audit_effective_setup_sample.ps1
```

The default command verifies the frozen augmented-Train SHA-256 and writes the
IMP-082 report. It uses maximum-cardinality half-open interval scheduling and
cannot read Validation/Test, train a model, modify Runtime/Risk, or authorize
Deployment. To reproduce the updated score and its delta from IMP-080:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\build_research_scorecard.ps1 `
  -MetricsPath training\config\research_scorecard_imp082_effective_sample.json `
  -ScorecardPath training\output\research_scorecard_imp082_effective_sample\research_scorecard.json `
  -ReferencePath training\output\research_scorecard_current\research_scorecard.json
```

## Effective Entry/Stop expectancy diagnostic

After IMP-082 passes G1, reproduce the Effective-Train expectancy, MFE/MAE,
drawdown, and loss-tail evidence with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\diagnose_entry_stop_expectancy.ps1
```

The command verifies both frozen SHA-256 values, uses the 232-record maximum
non-overlapping sample, and emits a deterministic moving-block 95% confidence
interval. It cannot read Validation/Test, select a Candidate, train a model,
or change Runtime/Risk/Deployment. The completed IMP-083 result identifies
favorable-excursion giveback but requires a causal M5/real-tick lifecycle
replay before any Breakeven or Trailing rule may be proposed.

## Causal M5 lifecycle-management replay

IMP-084 freezes the Baseline, cost-covered Breakeven after a completed `+1R`
M5 close, and a two-stage `+1R/+2R` Ratchet before M5 paths are collected.
Prepare the 232 hash-sealed requests and copy them to MT5 with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\prepare_lifecycle_path_research.ps1
```

Compile and sync the offline exporter with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\compile_lifecycle_path_research.ps1
```

Attach `TestPastOnlyLifecyclePathExporter` once to an XAUUSD chart. It exports
only mature M5 OHLC paths, reports `deployment=false`, and removes itself.
Then collect and replay with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\collect_lifecycle_path_research.ps1
```

Same-M5 Target/active-Stop collisions are quarantined. The replay applies the
frozen 1.00x/1.25x/1.50x cost stress and cannot read Validation/Test, alter
Runtime/Risk, send orders, start Forward, or authorize Deployment.

The completed 232-request replay passed exact Baseline parity. Breakeven Mean R
was `-0.079R` and two-stage Ratchet Mean R was `-0.125R`, versus Baseline
`-0.074R` at 1.00x cost. Both Candidates failed the frozen Train gates and were
rejected. The accepted Baseline, Runtime, and `NO-GO` state remain unchanged.

IMP-085 attributes the paired difference with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\diagnose_lifecycle_differential_attribution.ps1
```

At 1.00x, Breakeven saved 42 Baseline Stops but clipped 17 Baseline Targets,
for `-1.084R` net Delta. Ratchet saved 42 Stops but clipped 22 Targets, for
`-7.032R` net Delta. Subgroup results are descriptive only and cannot authorize
a filter or Runtime rule.

## Canonical Setup-response attribution

IMP-086 tests whether the approved Schema 4.0.0 Trend, Volatility, Liquidity,
and Session groups distinguish the four causal lifecycle response classes:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\run_canonical_setup_response_attribution.ps1
```

The command verifies all frozen hashes, uses only the 232 non-overlapping
Effective-Train records, recomputes IMP-085 class parity, runs four expanding
past-only folds, and writes fixed-bucket explanations. It cannot read
Validation/Test, select a threshold/filter, train a Runtime model, change
Risk, or authorize Deployment.

No canonical group passed the pre-registered readiness gate. Volatility was
least weak with `+0.007` support gain, `0.287` balanced Accuracy, and `0.259`
Macro F1, but only one of four folds was positive and a minority class had zero
recall. Therefore no confirmation hypothesis or Candidate was selected and
the accepted Baseline remains `NO_GO_TRAIN` at Overall Readiness `49/100`.

## Existing Entry geometry outcome attribution

IMP-087 strictly joins accepted Effective-Train outcomes to the frozen V1
Setup Audit and tests Trigger Shape, Entry/Invalidation, and Payoff Geometry:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\run_entry_geometry_outcome_attribution.ps1
```

The command verifies all source hashes and exact Entry/Stop/Target/POI/RR/cost
parity, evaluates four expanding past-only folds, and never reads Validation or
Test. No view passed: Payoff Geometry was least weak at only `+0.0017` support
gain, `0.514` balanced Accuracy, and `0.029` Target-first recall. Consequently
no reclaim, POI, cost, or RR threshold is authorized. New trigger-event path
evidence requires a separate approved tester-only exporter/schema change.

## Past-only M5 trigger-event evidence

IMP-088 is the approved outcome-blind evidence collector for the missing
trigger-event detail. Prepare its 232 hash-sealed requests with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\prepare_trigger_event_research.ps1
```

Sync and compile the isolated research EA with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\compile_trigger_event_research.ps1
```

Keep Algo Trading disabled and attach `TestPastOnlyTriggerEventExporter` once
to an XAUUSD chart. It replays the existing Brain ATR and confirmed swing
contract, exports only trigger/context and older M5 evidence, and removes
itself. Success is `Past-only trigger-event records written: 232`.

Broker suffixes are supported: the canonical request remains `XAUUSD`, while
the EA uses the chart `_Symbol` (for example `XAUUSD.sc`) as its data source
and records both identities in export schema 1.1. Leave `DataSymbol` blank to
use the current chart symbol.

Then collect and validate the Artifact with:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\collect_trigger_event_research.ps1
```

Request and export schemas contain no Outcome label. The collector cannot read
Validation/Test, train a model, change Feature Schema/Runtime/Risk, or
authorize Deployment.
