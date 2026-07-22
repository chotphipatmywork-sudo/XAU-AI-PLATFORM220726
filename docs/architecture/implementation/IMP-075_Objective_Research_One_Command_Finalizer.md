# IMP-075 Objective Research One-Command Finalizer

Version: 1.0.0

Date: 2026-07-20

Status: Implemented; focused validation and real evidence run passed

Architecture Baseline: ABR-1.0

Related: CR-013, CR-014, IMP-070, IMP-072, IMP-073, IMP-074

## Purpose

Remove repeated operator work without weakening any evidence gate. One command
now archives the latest Objective Tester artifacts, records hashes, verifies
MT5 real-tick warning coverage, builds and splits Setup outcomes, compares the
candidate with the reference using Train only, and runs a fixed residual
diagnostic.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
  -File .\tools\finalize_objective_research_run.ps1 `
  -OutputName <unique_evidence_name>
```

## Fail-closed controls

- every MT5 daily real-tick warning date must exist in the versioned exclusion
  file before Dataset construction;
- raw Tester artifacts are copied before analysis and recorded in a SHA-256
  manifest;
- the Dataset builder reads the archived copy, not mutable later Tester files;
- contract comparison accepts filenames containing Train only and rejects
  Validation/Test inputs;
- insufficient Train size remains a hard refusal;
- diagnostics cannot train a model, change Runtime, or authorize deployment.

## Residual diagnostic boundary

The residual diagnostic registers ten observation-time questions before
evaluation. It uses three chronological descriptive blocks and requires at
least five matches per block, 20 aggregate matches, consistent expected signs,
at least five percentage points Target-rate effect, and at least 0.10R mean
effect before naming a fresh-confirmation priority. The evidence is reused
historical Train data, so even a priority cannot change the Setup contract.

The completed 182-row Train run retained two priorities:

- early Session (`session_progress <= 25`): 44 matches, 40.91% Target rate,
  +0.623R mean, +15.63 percentage-point and +0.688R lifts;
- late Session (`session_progress >= 75`): 44 matches, 4.55% Target rate,
  -0.845R mean, -20.73 percentage-point and -0.781R lifts.

These repeat the earlier CR-014 Session observation and are not independent
confirmation. The strong directional Trend result failed the material-effect
gate. Validation/Test remain unused for selection and deployment remains
`NO_GO`.

## Files

- `tools/finalize_objective_research_run.ps1`
- `tools/build_stage_d_setup_outcomes.ps1`
- `training/audit_real_tick_quality.py`
- `training/compare_objective_contract_train.py`
- `training/diagnose_objective_reclaim_residuals.py`
- three focused Python tests with matching names

No MQL5 source or Runtime contract changed in IMP-075, so MetaEditor compilation
is not applicable. Existing MQL5 compile evidence from IMP-074 remains valid.

## Validation result

- all three focused offline tests passed;
- PowerShell parsing passed for the finalizer and extended Dataset builder;
- the finalizer completed against the preserved five-year real-tick evidence;
- all 16 warned daily dates were covered by versioned exclusions;
- archived-source Dataset/Split reproduced 262 plans and 260 trainable rows;
- the complete Python regression passed 43/43.

The first live-evidence attempt correctly failed closed when the parser treated
an aggregate date range as a daily warning. The parser was narrowed to MT5
single-day warning syntax and a regression case now protects that distinction.
