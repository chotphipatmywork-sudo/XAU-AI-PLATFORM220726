# ADR-006 Strategy Setup and Trade Plan Boundary

Version: 1.3.0

Date: 2026-07-18

Status: Stage C validated; minimum-reclaim contract review approved

Architecture Baseline: ABR-1.0

## Context

The platform has a safe canonical Runtime and Shadow Execution path, but its
current fixed-distance paper plan cannot represent a structural invalidation
level or a nearest structural target. Putting entry-location logic in Brain,
Risk, or Execution would violate existing ownership boundaries.

## Decision

Strategy Setup research belongs inside AI Runtime ownership and is separated
into three contracts:

- Setup Context: past-only confluence and structural price evidence;
- Setup Candidate: accepted directional opportunity;
- Trade Plan: proposed Entry, Stop, Target, cost-adjusted risk, reward, and RR.

The top-level canonical path remains:

`Market -> Brain -> AI Runtime -> Decision -> Risk -> Execution -> Trade Lifecycle`

The approved future internal AI Runtime sequence is:

`Brain context -> Strategy Setup -> AI quality evaluation -> Trade Plan proposal`

CR-013 Stage A implements and tests only Strategy Setup and Trade Plan contracts.
It does not connect them to the canonical Runtime.

CR-013 Stage B may add an internal pure adapter from existing closed-bar M15
Trend and confirmed M5 swing/trigger evidence into the Stage A Setup Context.
It may expose objective research evidence but may not query broker state,
approve Risk, mutate Execution, read Dataset outcomes, or connect itself to the
canonical Runtime. Stage C requires a separate integration review.

The project owner approved that Stage C review on 2026-07-18. Stage C may add a
tester-only provider mode and an Execution-owned structural price-plan contract.
Runtime may convert an accepted AI Trade Plan into that Execution contract only
after calling the unchanged Risk gate. Shadow Execution may consume it only
when Risk explicitly allows the trade. No Forward or broker path is approved.

On 2026-07-19 the project owner approved one evidence-backed Setup-contract
correction after IMP-073 passed its frozen Train-only four-fold gate. A
completed M5 directional reclaim must now reach at least `0.10 * ATR_M5` before
the trigger is actionable. This remains deterministic Setup evidence; it is
not an AI Feature, Risk permission, or deployment authorization.

## Ownership

- Brain owns market understanding and confirmed market structures.
- Strategy Setup owns deterministic confluence acceptance.
- AI evaluation may later own setup-quality probability, not Risk permission.
- Trade Planning owns proposed structural Entry, Stop, and Target geometry.
- Risk owns final permission and future position-sizing constraints.
- Execution owns synthetic or broker mutation and may consume only a Risk-approved
  plan after a later integration approval.

## Rules

- completed-bar inputs only;
- no future data or Dataset access in Runtime planning;
- no arbitrary AI-generated Stop or Target;
- nearest verified structural target is conservative by default;
- estimated costs reduce reward and increase risk;
- plan validation is not Risk approval;
- Feature, Label, Confidence, Setup, Risk, and Result data remain separate;
- no Forward or live behavior change in Stage A or Stage B.
- completed reclaim distance must be at least `0.10 * ATR_M5`;
- Stage C is Strategy Tester-only and must fail initialization outside Tester;
- structural paper prices may be consumed only after explicit Risk approval;
- Execution may reject unsafe geometry/RR but may not create or alter strategy
  Stop/Target levels.

## Consequences

- adaptive RR can be evaluated without moving strategy logic into Execution;
- CR-012 fixed 1:2 remains an unchanged benchmark;
- future detector and Runtime integration work has explicit input/output
  contracts;
- additional focused tests and an integration approval are required before a
  Trade Plan can affect Shadow Execution.

## Validation

- synthetic BUY and SELL plans validate correct geometry;
- higher structural RR is preserved;
- insufficient RR and incomplete confluence are rejected;
- broker mutation and reverse dependencies remain absent;
- MetaEditor reports zero errors and zero warnings for the focused test.
