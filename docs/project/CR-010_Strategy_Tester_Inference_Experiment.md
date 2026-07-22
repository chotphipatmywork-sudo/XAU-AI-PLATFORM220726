# CR-010 Strategy Tester Inference Experiment

Version: 1.0.0

Date: 2026-07-17

Status: Approved for implementation

Architecture Baseline: ABR-1.0

Related: CR-008, CR-009, ADR-005, Phase 8A.6

## Approval

The project owner explicitly approved a Strategy Tester-only inference
experiment. The Forward default must remain the locked legacy provider. This
approval does not authorize Forward use of the experimental provider, model
deployment, live execution, or broker mutation.

## Problem

Accepted full-period V4 evidence contains 1,895 valid closed-bar Decisions but
the legacy four-score provider emits no BUY. Approved labels contain 713 BUY
outcomes. Twelve-feature research candidates restore two-sided output but do
not meet the model-quality gate.

The platform needs an isolated way to exercise an alternate directional
provider through the complete canonical Shadow lifecycle and compare it with
the immutable legacy baseline without exposing Forward or live operation.

## Approved change

1. Add an explicit Shadow inference-provider mode to Runtime configuration.
2. Keep `LEGACY_LOCKED` as the default in every environment.
3. Add `DIRECTIONAL_RESEARCH` using the predeclared Trend composite:
   `0.45 regime + 0.40 momentum + 0.15 slope`.
4. Map scores below 40 to SELL, above 60 to BUY, and the middle band to HOLD.
5. Permit `DIRECTIONAL_RESEARCH` only when `MQL_TESTER` is true; Runtime
   initialization must fail if it is selected on a Forward chart.
6. Keep both providers at model status `NO_GO` and deployment authorization
   false.
7. Isolate every Directional Strategy Tester artifact from legacy artifacts.
8. Record provider identity and model status in Decision and Report evidence.

## Safety invariants

- Risk remains the final permission gate.
- Execution and lifecycle code are unchanged.
- No provider may call a broker API.
- The research provider cannot start outside Strategy Tester.
- Model and live deployment authorization remain false.
- The experiment cannot silently replace the default provider.

## Evidence comparison

The first comparison must use the same XAUUSD M15 real-tick interval and the
same Risk/Execution inputs as the accepted legacy V4 run. It measures
directional coverage and paper lifecycle behavior, not deployment eligibility.

## Rollback

Remove the Directional provider and provider input, restore the single locked
provider selection, and retain all isolated research artifacts. Legacy
Forward state and Decision evidence remain unaffected.

