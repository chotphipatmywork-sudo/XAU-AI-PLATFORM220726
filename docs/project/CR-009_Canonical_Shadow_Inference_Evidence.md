# CR-009 Canonical Shadow Inference Evidence

Version: 1.0.0

Date: 2026-07-17

Status: Approved for implementation

Architecture Baseline: ABR-1.0

Related Phase: Phase 8A.6 — Model Improvement and Deployment Gate

## Approval

The project owner approved adding the complete Feature Schema 4.0 vector to
canonical Shadow evidence and introducing an explicit AI inference-provider
boundary. This approval does not authorize a trained model, model deployment,
live execution, or any broker mutation.

## Problem

The canonical Shadow Runtime currently records only four development-heuristic
scores. The approved offline feature contract contains twelve dimensions:

- Trend: regime, momentum, slope
- Volatility: regime, change
- Liquidity: activity, range position, sweep direction
- Session: Asia, London, New York, progress

Without these values in the per-bar Shadow evidence, offline diagnosis cannot
compare Runtime observations with Feature Schema 4.0. The Runtime also calls
the development heuristic directly, which leaves no explicit controlled
boundary at which a future approved inference implementation can be inserted.

## Approved change

1. Project every valid Brain result through `CBrainFeatureAdapter` inside the
   canonical Runtime.
2. Create one inference request containing the twelve Schema 4.0 features and
   the four compatibility inputs required by the current heuristic.
3. Introduce `IAIInferenceProvider` and place the existing four-score
   heuristic behind `CDevelopmentHeuristicInferenceProvider`.
4. Preserve the current decision behavior exactly; this change creates
   evidence and a boundary, not a new model.
5. Record the feature-schema version, provider identity, deployment lock, all
   twelve features, and the four compatibility scores on every Decision row.
6. Use new versioned Decision filenames so existing evidence is never appended
   under a different CSV header.

## Runtime flow

`Market -> Brain -> Feature Adapter -> Inference Provider -> Decision -> Risk -> Shadow Execution -> Paper Trade Lifecycle`

Feature adaptation and provider selection remain inside the AI Runtime
boundary. Risk remains the final permission gate and Execution remains unable
to bypass it.

## Compatibility and locks

- Feature Schema remains `4.0.0`.
- Label Schema remains `1.1.0`.
- The active provider remains `DEVELOPMENT_HEURISTIC_4_SCALAR_NO_GO`.
- The compatibility inputs preserve the prior heuristic output.
- `ModelDeploymentAuthorized` remains false.
- `LiveExecutionAuthorized` remains false.
- Shadow code remains free of broker mutation APIs.
- Existing non-versioned Decision CSV files remain untouched as historical
  evidence.

## Evidence files

- Forward: `XAU_AI_SHADOW_DECISIONS_V4.csv`
- Strategy Tester: `XAU_AI_SHADOW_BACKTEST_DECISIONS_V4.csv`

## Validation

- A focused provider test must prove that the provider output matches direct
  evaluation by the existing heuristic for the same four compatibility
  inputs.
- The test must prove the provider identity, Feature Schema 4.0 request, and
  deployment lock.
- The canonical EA and all affected focused tests must compile with zero
  errors and zero warnings.
- Static closure validation must continue to find no broker mutation path.

## Rollback

Restore direct `CAIManager` ownership in `CRuntimeManager`, restore the prior
Decision audit signature and filenames, and remove the provider/request files.
The versioned V4 evidence files may be retained as immutable research evidence.
No broker or live position rollback is required.

