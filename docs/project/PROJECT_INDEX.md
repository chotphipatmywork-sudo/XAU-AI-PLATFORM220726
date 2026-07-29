# XAU AI PLATFORM Project Documentation Index

Version : 1.0.0

Status : FROZEN

Architecture Baseline : ABR-1.0

---

## Purpose

This document defines the official index of all project documentation within the XAU AI PLATFORM.

It provides the recommended reading order and acts as the entry point for developers, reviewers, and AI-assisted development workflows.

---

## Documentation Source of Truth

Project documentation is the official reference for:

- Architecture decisions.
- Development standards.
- Module contracts.
- Implementation rules.
- Governance processes.

All implementation activities must remain consistent with approved documentation.

---

## Foundation Documents

### Project Governance

| Document | Purpose |
| --- | --- |
| PROJECT_CONSTITUTION.md | Defines project principles and governance rules |
| PROJECT_STRUCTURE.md | Defines official repository structure |
| PROJECT_ROADMAP.md | Defines project development roadmap |

---

### Architecture Governance

| Document | Purpose |
| --- | --- |
| ARCHITECTURE_FREEZE.md | Defines frozen architecture baseline |
| ARCHITECTURE_DECISIONS.md | Records architecture decisions |
| DEPENDENCY_RULES.md | Defines dependency boundaries |

---

### Module Governance

| Document | Purpose |
| --- | --- |
| MODULE_INTERFACE_CATALOG.md | Defines approved public interfaces |
| MODULE_IMPLEMENTATION_GUIDE.md | Defines module implementation rules |
| PACKAGE_CONTRACT_TEMPLATE.md | Defines package contract template |
| PACKAGE_CREATION_CHECKLIST.md | Defines package creation validation |

---

### Development Governance

| Document | Purpose |
| --- | --- |
| BUILD_GUIDE.md | Defines build and validation process |
| DEFINITION_OF_DONE.md | Defines completion criteria |
| IMPLEMENTATION_CHECKLIST.md | Defines implementation validation |

---

### Change Management

| Document | Purpose |
| --- | --- |
| CHANGE_REQUEST.md | Defines architecture change process |
| INTERFACE_CHANGE_POLICY.md | Defines interface change rules |
| VERSIONING_POLICY.md | Defines version management rules |

---

### Review Process

| Document | Purpose |
| --- | --- |
| REVIEW_PROCESS.md | Defines review workflow |
| REVIEW_CHECKLIST.md | Defines review validation checklist |
| RELEASE_CHECKLIST.md | Defines release validation |

---

### Reference Documents

| Document | Purpose |
| --- | --- |
| GLOSSARY.md | Defines project terminology |

### Phase 7 Model Evidence

| Document | Purpose |
| --- | --- |
| MODEL_TRAINING_DEPLOYMENT_GATE_REVIEW.md | Records the model-quality gate evidence and deployment NO-GO |
| PHASE_7_MODEL_TRAINING_DEPLOYMENT_CLOSURE.md | Closes the authorized training workflow and defines deployment reopen conditions |
| CR-001_Feature_Schema_4_0_Session_Progress.md | Records the approved Schema 4.0 Session Progress change |
| CR-002_H1_Multi_Timeframe_Context.md | Records the rejected H1 context research proposal |
| CR-003_Liquidity_Temporal_Context.md | Defines the bounded research-only Liquidity event-memory proposal |
| CR-004_Temporal_Brain_Feature_Window.md | Defines the bounded full-Brain temporal-window research proposal |
| CR-005_Confirmed_Swing_Structure_Context.md | Defines confirmed swing-structure research without changing Runtime |
| CR-006_Past_Price_Action_Context.md | Defines bounded completed-bar price-action research without changing Runtime |
| CR-007_Price_Path_State.md | Defines bounded 16-bar completed price-path research without changing Runtime |
| CR-008_Shadow_Trading_Integration.md | Defines the approved non-broker Phase 8A Shadow integration and safety gates |
| CR-009_Canonical_Shadow_Inference_Evidence.md | Defines Schema 4.0 Shadow evidence and the locked inference-provider boundary |
| CR-010_Strategy_Tester_Inference_Experiment.md | Defines the isolated tester-only Directional provider experiment |
| CR-011_Completed_Tick_Microstructure_Context.md | Approves bounded completed-tick Liquidity/Volatility research after Phase 8A closure |
| CR-012_Simple_Baseline_Tester_Benchmark.md | Approves an isolated Strategy Tester-only Trend alignment benchmark with fixed 1:2 Shadow SL/TP |
| CR-013_Hybrid_Rule_AI_Entry_Research.md | Approves bounded Strategy Setup and structure-aware Trade Plan research inside AI Runtime ownership |
| CR-014_Dual_Direction_Structural_Setup_Research.md | Registers bounded Train-only Setup V2 continuation/reversal research without Runtime authority |
| SHADOW_TRADING_RUNBOOK.md | Operator guide for safe compile, focused tests, Demo observation, and evidence review |
| PHASE_8A_SHADOW_GATE_REVIEW.md | Records the Strategy Tester/Forward safety PASS and model-quality NO-GO |
| PHASE_8A_SHADOW_CLOSURE.md | Closes Phase 8A with operational PASS and deployment denied |
| ../architecture/implementation/IMP-060_Canonical_Shadow_Strategy_Tester.md | Defines isolated canonical EA Strategy Tester evidence and its safety report |
| ../architecture/implementation/IMP-061_Canonical_Shadow_Inference_Evidence.md | Implements versioned 12-feature evidence without changing the locked heuristic |
| ../architecture/implementation/IMP-062_Strategy_Tester_Inference_Experiment.md | Implements safe provider selection and isolated Directional test artifacts |
| ../architecture/adr/ADR-006_Strategy_Setup_Trade_Plan_Boundary.md | Defines Setup Candidate and Trade Plan ownership while preserving Risk and Execution boundaries |
| ../architecture/implementation/IMP-066_Hybrid_Rule_Structure_Aware_Trade_Plan.md | Implements CR-013 Stage A contracts and focused validation |
| ../architecture/implementation/IMP-067_Historical_Runtime_Session_Parity.md | Corrects completed-bar Session observation parity between historical replay and Runtime |
| ../architecture/implementation/IMP-068_Objective_M15_M5_Setup_Adapter.md | Implements the CR-013 Stage B past-only M15/M5 Setup adapter |
| ../architecture/implementation/IMP-069_Objective_Setup_Strategy_Tester_Integration.md | Integrates the objective setup into Risk-gated Strategy Tester Shadow execution |
| ../architecture/implementation/IMP-070_Setup_Outcome_Dataset_And_Quality_Ranker.md | Defines the separate Stage D setup-outcome Dataset, leakage gates, and Train-only quality ranker |
| ../architecture/implementation/IMP-071_Setup_V2_Train_Only_Hypothesis_Diagnostic.md | Implements CR-014 fixed-question Train-only diagnostics and records the Stage 1 NO-GO |
| ../architecture/implementation/IMP-072_Fresh_Session_Hypothesis_Confirmation.md | Freezes one-shot post-cutoff Session confirmation without opening sealed partitions |
| ../architecture/implementation/IMP-073_Objective_Setup_Failure_Diagnostic.md | Diagnoses frozen Train-only Setup geometry and identifies the strong-reclaim review candidate |
| ../architecture/implementation/IMP-074_Objective_Minimum_Reclaim_Contract.md | Implements the approved symmetric 0.10 ATR Objective reclaim threshold and validation gate |
| ../architecture/implementation/IMP-075_Objective_Research_One_Command_Finalizer.md | Automates Objective archival, real-tick quality audit, Dataset/Split, Train comparison, and residual diagnostics |
| ../architecture/HYBRID_PROFESSIONAL_TRADING_QUESTION_CATALOG.md | Defines professional Hybrid questions, data, calculations, ownership, and future-leakage controls |

---

## Recommended Reading Order

New contributors should read documents in the following order:

1. PROJECT_INDEX.md
2. PROJECT_CONSTITUTION.md
3. PROJECT_STRUCTURE.md
4. ARCHITECTURE_FREEZE.md
5. ARCHITECTURE_DECISIONS.md
6. DEPENDENCY_RULES.md
7. MODULE_INTERFACE_CATALOG.md
8. MODULE_IMPLEMENTATION_GUIDE.md
9. CODING_STANDARD.md
10. CODEX_WORK_RULES.md
11. BUILD_GUIDE.md
12. DEFINITION_OF_DONE.md
13. CHANGE_REQUEST.md

---

## AI Development Workflow

The approved development workflow is:

```text
Architecture
      ↓
Documentation
      ↓
Coding Standard
      ↓
Implementation
      ↓
Compile Validation
      ↓
Testing
      ↓
Review
      ↓
Completion
```

Documentation Maintenance Rules

All documentation updates must:

Follow MARKDOWN_STANDARD.md.
Maintain version information.
Preserve ownership information.
Update change history when required.
Remain consistent with Architecture Freeze.
Project Status

Current Phase:

Foundation Architecture

Architecture Status:

FROZEN

Baseline:

ABR-1.0

Document Review Status

Document:

PROJECT_INDEX.md

Review Phase:

Phase 0.3 — Foundation Architecture Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Next Review:

Documentation Consistency Audit

Document Ownership

Owner:

XAU AI PLATFORM Architecture Team

Document Type:

Project Governance Document

Maintained By:

Project Documentation Governance Process

Authority:

This document is governed by:

PROJECT_CONSTITUTION.md
ARCHITECTURE_FREEZE.md
DOCUMENTATION_GOVERNANCE.md
Change History

Related active research change requests:

- `CR-015_Pre_Train_History_Augmentation.md`: isolated pre-Train real-tick
  evidence collection with frozen Validation/Test hashes and permanent NO-GO.
- `../architecture/implementation/IMP-076_CR015_Pre_Train_Augmentation.md`:
  fail-closed offline augmentation with opaque sealed-partition hash checks.
- `CR-016_Two_Bar_M5_Continuation_Confirmation.md`: rejected frozen
  tester-only two-bar M5 entry-confirmation candidate; its real-tick smoke run
  reached zero valid structural plans and retained permanent NO-GO locks.
- `../architecture/implementation/IMP-077_Two_Bar_M5_Continuation_Confirmation.md`:
  isolated implementation, Audit V2 compatibility, compile evidence, and the
  fail-closed real-tick smoke rejection.
- `CR-017_Pre_Trigger_M5_Reversal_Context.md`: rejected frozen tester-only
  reversal-context candidate; Entry returned to the trigger close but all
  smoke candidates remained below the unchanged minimum `2.0R`.
- `../architecture/implementation/IMP-078_CR017_Pre_Trigger_Reversal_Context.md`:
  causal context/trigger mapping, Setup Audit V3, implementation evidence, and
  the fail-closed real-tick smoke rejection.
- `../architecture/implementation/IMP-079_Offline_Structural_Opportunity_Research.md`:
  completed Train-only Entry/Stop/Target diagnosis confirming low structural
  plan reachability and requiring multi-level past-only Target evidence before
  another Runtime candidate; Validation/Test remain opaque.
- `../architecture/implementation/IMP-080_Past_Only_Multilevel_Structural_Target_Replay.md`:
  completed isolated M5/M15 confirmed Target-ladder replay; all seven
  Target-only candidates failed the frozen Train gate and no Runtime CR or
  Deployment was authorized.
- `RESEARCH_SCORECARD_STANDARD.md`: active RSCS-1.0 weights, Hard Gates,
  Baseline/Candidate progression rules, and required Before/After ledger.
- `../architecture/implementation/IMP-081_Research_Scorecard_Automation.md`:
  strict automated scorecard calculation; current Overall Readiness is 49/100
  and remains Train NO-GO.
- `../architecture/implementation/IMP-082_Effective_Setup_Sample_Audit.md`:
  strict Train-only overlap audit; 232/233 non-overlapping outcomes pass G1,
  while negative expectancy keeps Overall Readiness at 49/100 and NO-GO.
- `../architecture/implementation/IMP-083_Effective_Entry_Stop_Expectancy_Diagnostic.md`:
  audited 232-record expectancy, moving-block confidence interval, drawdown,
  loss tail, and favorable-excursion giveback; no Candidate or CR authorized.
- `../architecture/implementation/IMP-084_Causal_M5_Lifecycle_Management_Replay.md`:
  completed 232-request Train-only M5 replay; cost-covered Breakeven and
  two-stage Ratchet Candidates were rejected, with Initial Risk and all
  Runtime/Deployment locks unchanged.
- `../architecture/implementation/IMP-085_Lifecycle_Differential_Attribution.md`:
  paired causal attribution shows saved Stop value was outweighed by clipped
  Target value; no post-hoc subgroup filter or new lifecycle rule authorized.
- `../architecture/implementation/IMP-086_Canonical_Setup_Response_Attribution.md`:
  completed past-only response separability across the four canonical feature
  groups; none passed the frozen confirmation gate, so no filter, Candidate,
  Runtime change request, or Deployment was authorized.
- `../architecture/implementation/IMP-087_Existing_Entry_Geometry_Outcome_Attribution.md`:
  strict Train-only attribution of existing Trigger, Entry/Invalidation, and
  Payoff Geometry; all views failed Target recall and stability gates, so no
  threshold or Runtime Candidate was authorized.
- `../architecture/implementation/IMP-088_Past_Only_M5_Trigger_Event_Evidence.md`:
  approved outcome-blind tester-only exporter for missing M5 trigger/context,
  POI-touch, and structural-age evidence; compile-clean and awaiting one MT5
  collection run with Deployment locked false.

Version Date    Change Description
1.0.0   Phase 0.3   Initial Project Documentation Index created
## Current-feed research

- [IMP-089 Current-Feed Setup Funnel Diagnostic](../architecture/implementation/IMP-089_Current_Feed_Setup_Funnel_Diagnostic.md)
- [IMP-090 Current-Feed Past-Only Target Ladder](../architecture/implementation/IMP-090_Current_Feed_Past_Only_Target_Ladder.md)
- [IMP-091 Current-Feed Entry/Stop Diagnostic](../architecture/implementation/IMP-091_Current_Feed_Entry_Stop_Diagnostic.md)
- [IMP-092 Current-Feed Causal M5 Lifecycle](../architecture/implementation/IMP-092_Current_Feed_Causal_M5_Lifecycle.md)
- [IMP-093 Current-Feed Past-Only Stop Ladder](../architecture/implementation/IMP-093_Current_Feed_Past_Only_Stop_Ladder.md)
- [IMP-094 Current-Feed Direction Asymmetry Audit](../architecture/implementation/IMP-094_Current_Feed_Direction_Asymmetry_Audit.md)
- [IMP-095 Current-Feed Joint Geometry Frontier](../architecture/implementation/IMP-095_Current_Feed_Joint_Geometry_Frontier.md)
- [IMP-096 Current-Feed Joint Geometry M5 Causal Replay](../architecture/implementation/IMP-096_Current_Feed_Joint_Geometry_M5_Causal_Replay.md)
- [IMP-097 Current-Feed RR Rejection Root Cause](../architecture/implementation/IMP-097_Current_Feed_RR_Rejection_Root_Cause.md)
- [IMP-098 Structural Stop-to-Target Imbalance Root Cause](../architecture/implementation/IMP-098_Structural_Stop_Target_Imbalance_Root_Cause.md)
- [IMP-099 Train-only Geometry Component Experiment Preregistration](../architecture/implementation/IMP-099_Train_Only_Geometry_Component_Experiment_Preregistration.md)
- [IMP-100 Train-only Geometry Causal Replay](../architecture/implementation/IMP-100_Train_Only_Geometry_Causal_Replay.md)
- [PER-100 Post-Experiment Review](../architecture/implementation/PER-100_Post_Experiment_Review.md)
- [IMP-101 Post-Entry Behaviour Research Design](../architecture/implementation/IMP-101_Research_Design.md)
- [IMP-101A Diagnostic Data Specification](../architecture/implementation/IMP-101A_Diagnostic_Data_Specification.md)
- [IMP-101C Diagnostic Analysis](../architecture/implementation/IMP-101C_Diagnostic_Analysis.md)
- [IMP-101C Statistical Appendix](../architecture/implementation/IMP-101C_Statistical_Appendix.md)

## Replacement artifact governance

- [Replacement Canonical Artifact Specification](../architecture/implementation/REPLACEMENT_CANONICAL_ARTIFACT_SPECIFICATION.md)
- [Replacement Artifact Identity Record](../architecture/implementation/REPLACEMENT_ARTIFACT_IDENTITY.md)
- [Replacement Implementation Plan](../architecture/implementation/REPLACEMENT_IMPLEMENTATION_PLAN.md)
- [Replacement Execution Authorization](../architecture/implementation/REPLACEMENT_EXECUTION_AUTHORIZATION.md)
- [Replacement Artifact Storage Policy](../architecture/implementation/REPLACEMENT_ARTIFACT_STORAGE_POLICY.md)
- [Replacement Manifest Contract](../architecture/implementation/REPLACEMENT_MANIFEST_CONTRACT.md)
- [Replacement Architecture Review](../architecture/implementation/REPLACEMENT_ARCHITECTURE_REVIEW.md)
- [Replacement Technical Review](../architecture/implementation/REPLACEMENT_TECHNICAL_REVIEW.md)
- [Replacement Project Approval](../architecture/implementation/REPLACEMENT_PROJECT_APPROVAL.md)
- [Replacement Governance Decision](../architecture/implementation/REPLACEMENT_GOVERNANCE_DECISION.md)
