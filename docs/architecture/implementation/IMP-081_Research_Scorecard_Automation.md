# IMP-081 Research Scorecard Automation

Version: 1.0.0

Date: 2026-07-22

Status: Implemented; current Baseline scored; NO-GO

Architecture Baseline: ABR-1.0

Related: RSCS-1.0, CR-013, IMP-075, IMP-079, IMP-080

## Purpose

Implement the project-wide RSCS-1.0 calculator so every new Baseline and
Candidate is measured with identical frozen weights, strict unknown handling,
reference deltas, and non-compensating Hard Gate caps.

## Implementation

- `training/research_scorecard.py` validates an exact versioned input schema,
  calculates all component scores, applies G0-G8, and optionally compares with
  a prior scorecard;
- `training/test_research_scorecard.py` covers the current negative Baseline,
  perfect-but-unauthorized evidence, invalid causality, uncertain positive
  expectancy, reference deltas, and schema fail-closure;
- `training/config/research_scorecard_imp080_current.json` freezes the current
  IMP-080 Baseline inputs and evidence hashes;
- `tools/build_research_scorecard.ps1` provides the repeatable entry point.

## Safety and architecture

This implementation is offline governance tooling only. It does not modify
MQL5, Brain, AI Runtime, Decision, Risk, Execution, Feature/Label schemas,
Forward configuration, broker state, or Deployment authorization. A scorecard
cannot enable Runtime or Deployment.

## Current result

RSCS-1.0 calculates Research Quality `90.00`, Strategy Evidence `12.50`,
Operational Safety `100.00`, and raw overall `53.25`. Failed Train gates cap
Overall Readiness at `49.00` with status `NO_GO_TRAIN`. Baseline promotion and
Deployment authorization are false.

## Validation

The focused synthetic scorecard test passed. The complete Python regression
then passed `48/48`, and PowerShell parsing passed for the wrapper. The wrapper
also generated the current scorecard through the same venv entry point and
space-containing Workspace path. No MetaEditor target is affected because no
MQL5 source changes in IMP-081; the last verified Runtime compile remains
`0 errors, 0 warnings`.
