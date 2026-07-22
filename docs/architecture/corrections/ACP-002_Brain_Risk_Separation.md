# ACP-002 Brain Risk Separation

Version: 1.0.0

Status: Draft

Architecture Baseline: ABR-1.0

---

## Purpose

This Architecture Correction Plan defines the refactoring required to establish a strict separation between the Brain and Risk modules.

The objective is to ensure that Brain produces trading intelligence only, while Risk independently evaluates and approves or rejects trading decisions.

---

## Related Findings

### Codex Architecture Compliance Audit Round 2

| Finding   | Severity | Description                                 |
| --------- | -------- | ------------------------------------------- |
| Finding 3 | B        | Brain owns Risk analysis and RiskResult     |
| Finding 4 | C        | Decision depends on RiskResult              |
| Finding 6 | B        | Execution receives no Risk-approved request |

---

## Related Architecture Decisions

* ADR-002 Module Dependency Direction
* ADR-003 Risk Boundary
* ADR-004 Execution Ownership

---

## Objective

Separate responsibilities according to the approved business pipeline.

Approved flow:

```text
Market

↓

Brain

↓

AI Runtime

↓

Decision

↓

Risk

↓

Execution
```

Brain shall never perform Risk evaluation.

Decision shall never depend on Risk.

Risk shall evaluate the completed Decision.

---

## Current State

Current implementation mixes responsibilities across Brain, Decision, and Risk.

Examples include:

* Brain instantiates Risk components.
* Brain produces RiskResult.
* Decision consumes RiskResult.
* Execution receives incomplete Risk information.

This creates reverse dependencies and violates the approved architecture.

---

## Target State

Module ownership shall be:

### Brain

Responsible for:

* Market context
* Pattern recognition
* Signal generation
* Confidence estimation
* Decision proposal

Brain shall not own:

* Risk approval
* Position sizing
* Exposure validation
* Trade permission

---

### Decision

Responsible for:

* Producing a complete trading decision

Decision shall not:

* Read RiskResult
* Perform Risk evaluation
* Reject trades based on Risk

---

### Risk

Responsible for:

* Position sizing
* Exposure validation
* Drawdown protection
* Trading approval
* Risk constraints

Risk receives a completed Decision and produces a Risk-approved result.

---

### Execution

Execution accepts only a Risk-approved trading request.

Execution shall not calculate:

* Position size
* Risk score
* Trade approval

---

## Root Cause Analysis

Earlier development stages embedded Risk analysis inside Brain to simplify execution flow.

As the architecture evolved, these temporary responsibilities remained, resulting in:

* Mixed module ownership
* Reverse dependency direction
* Tight coupling
* Reduced maintainability

---

## Files Expected To Be Modified

Potential implementation targets include:

```text
core/brain/

core/decision/

core/risk/

core/execution/
```

Specific files shall be confirmed before implementation.

---

## Refactoring Strategy

### Step 1

Remove Risk ownership from Brain.

---

### Step 2

Remove RiskResult from Brain output models.

---

### Step 3

Remove Risk dependencies from Decision.

---

### Step 4

Move Risk evaluation after Decision generation.

---

### Step 5

Create a Risk-approved request for Execution.

---

## Risks

Potential implementation risks include:

* Interface changes
* Model refactoring
* Pipeline integration updates
* Temporary compilation failures

Changes shall be completed incrementally and validated after each step.

---

## Validation Criteria

This correction is complete when:

* Brain contains no Risk types.
* Brain produces no RiskResult.
* Decision has no Risk dependency.
* Risk evaluates Decision independently.
* Execution accepts only Risk-approved requests.
* Codex reports no Finding 3.
* Codex reports no Finding 4.
* Codex reports no Finding 6.

---

## Completion Checklist

| Item                          | Status |
| ----------------------------- | ------ |
| Brain separated from Risk     | ☐      |
| RiskResult removed from Brain | ☐      |
| Decision independent of Risk  | ☐      |
| Risk evaluation relocated     | ☐      |
| Execution interface updated   | ☐      |
| Codex verification passed     | ☐      |
| ACP approved                  | ☐      |

---

## Exit Criteria

ACP-002 may be closed only after all related findings have been resolved and the implementation complies with ADR-002, ADR-003, and ADR-004.
