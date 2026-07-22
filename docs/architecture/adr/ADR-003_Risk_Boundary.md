# ADR-003 Risk Boundary

Version: 1.0.0

Status: Approved Draft

Architecture Baseline: ABR-1.0

---

## Context

The XAU-AI-PLATFORM Core Audit identified a responsibility boundary violation between the Brain module and the Risk module.

The observed issue:

```text id="4zq2pk"
BrainAnalyzer

↓

RiskResult
```

This creates an incorrect responsibility relationship.

The Brain module is responsible for market understanding and decision proposal.

The Risk module is responsible for capital protection, risk validation, and trade permission.

These responsibilities must remain separated before Architecture Freeze.

---

## Decision

The XAU-AI-PLATFORM architecture separates market intelligence, decision generation, and risk control into independent layers.

The approved flow is:

```text id="1j4jye"
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

Risk evaluation happens after a trading decision proposal and before execution.

---

## Brain Responsibility

The Brain module is responsible for:

* Market context analysis
* Market structure interpretation
* Signal analysis
* Pattern recognition
* Decision proposal generation

Brain output represents:

```text id="d2q4e6"
Market Understanding

+

Trading Opportunity Proposal
```

Brain must not perform:

* Risk approval
* Position sizing
* Capital allocation
* Exposure control
* Order execution

---

## AI Runtime Responsibility

AI Runtime processes:

* Brain output
* Features
* Market context

AI Runtime provides:

* Confidence scoring
* Decision support
* Intelligence enhancement

AI Runtime does not replace Risk control.

---

## Decision Responsibility

Decision module converts analysis into trading intent.

Examples:

```text id="z8p2f4"
BUY

SELL

HOLD
```

Decision represents:

* What action may be taken

Decision does not represent:

* Permission to trade

Risk approval is still required.

---

## Risk Responsibility

Risk module is the final safety gate before execution.

Risk owns:

* Risk validation
* Position sizing
* Exposure limits
* Account protection rules
* Trade permission

Risk input:

```text id="tq4t3k"
Trading Decision
```

Risk output:

```text id="2a2s8j"
Approved

or

Rejected
```

---

## Execution Boundary

Execution receives only risk-approved decisions.

Approved flow:

```text id="r2w4pv"
Decision

↓

Risk Approval

↓

Execution

↓

Trade Lifecycle
```

Execution must not bypass Risk.

---

## Prohibited Responsibilities

The following patterns are prohibited:

### Brain Controlling Risk

```text id="g4y8v6"
Brain

↓

Risk Approval
```

---

### Risk Performing Market Analysis

```text id="9x5p8j"
Risk

↓

Market Interpretation
```

---

### Execution Bypassing Risk

```text id="q0z5dk"
Decision

↓

Execution
```

---

## Consequences

### Positive Consequences

* Clear responsibility separation
* Safer trading decisions
* Easier testing
* Reduced coupling
* Better auditability

---

### Negative Consequences

* Existing Brain components may require refactoring
* Risk interfaces may need redesign

---

## Validation Criteria

The architecture is compliant when:

* Brain contains no Risk approval logic
* Risk receives decisions instead of market analysis
* Execution requires Risk approval
* Position sizing exists only inside Risk responsibility
* Codex audit confirms boundary compliance

---

## Related Decisions

Related ADRs:

* ADR-001 Canonical Runtime Path
* ADR-002 Module Dependency Direction
* ADR-004 Execution Ownership

---

## Decision Status

```text id="v0o4f1"
Risk Boundary: APPROVED

Architecture Freeze Impact:
Required Before Freeze
```
