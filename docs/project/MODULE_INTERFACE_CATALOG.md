# XAU AI PLATFORM — MODULE INTERFACE CATALOG

Version : 1.0.0

Status : Foundation

Architecture Baseline : ABR-1.0

---

## Purpose

This document defines the public interface contract
between modules inside the XAU AI PLATFORM.

The purpose is to establish clear boundaries between
architecture modules and prevent uncontrolled coupling
during implementation.

This document defines:

- Module responsibilities
- Public interface ownership
- Allowed communication paths
- Dependency boundaries
- Forbidden dependencies

This document acts as the bridge between:

```text
Architecture Rules
        ↓
Module Boundaries
        ↓
Public Interface Contracts
        ↓
Implementation
Scope

This document applies to all major modules inside
the XAU AI PLATFORM.

Covered modules:

Market Module
Indicator Module
Data Module
Brain Module
AI Runtime Module
Risk Module
Money Module
Execution Module
Position Module
Trade Lifecycle Module
Portfolio Module
Learning Module

This document does not define:

Internal implementation details
Private classes
Algorithm implementation
Trading strategy parameters
Optimization configuration

Those responsibilities belong to their respective
implementation documents.

Interface Principles
Single Responsibility

Each module must have one clearly defined responsibility.

A module must not:

Duplicate another module responsibility
Contain unrelated business logic
Replace another module function
Public Interface Only

Modules communicate through defined public interfaces.

A module must not:

Access internal implementation directly
Depend on private classes
Bypass interface contracts
Dependency Direction

Dependencies must follow the approved architecture direction.

Required flow:

Market
   ↓
Brain
   ↓
AI Runtime
   ↓
Risk
   ↓
Execution
   ↓
Trade Lifecycle
   ↓
Portfolio
   ↓
Learning

Reverse dependency is prohibited.

Interface Stability

Public interfaces are architecture contracts.

Changes to public interfaces require:

Review
Impact analysis
Change approval
No Hidden Coupling

Modules must not create hidden dependencies through:

Direct file access
Shared internal state
Undocumented communication
Duplicate data ownership
Contract Rules
Every Module Must Define

Each module must have:

Responsibility
Public Interface
Allowed Consumers
Allowed Dependencies
Forbidden Dependencies
Interface Ownership

Every public interface must have exactly one owner.

Example:

Interface
    ↓
Owner Module
    ↓
Consumers

Multiple ownership is prohibited.

Consumer Limitation

A module may only consume interfaces explicitly approved
in this catalog.

Unknown dependency requires architecture review.

Implementation Independence

Consumers must depend on interface contracts,
not concrete implementation.

Change Control

Any modification affecting:

Module boundary
Public interface
Dependency direction

must follow the project Change Request process.

Module Interface Registry
Market Module
Responsibility

The Market Module provides normalized market information
for higher-level analysis modules.

The module is responsible for:

Market data representation
Price context availability
Market state information
Time and session context

The Market Module does not make trading decisions.

Public Interface

Primary Interface:

IMarketProvider
Allowed Consumers

The following modules may consume Market interfaces:

Brain Module
Indicator Module
Data Module
Allowed Dependencies

The Market Module may depend on:

Data Module
Infrastructure Module
Common Utilities
Forbidden Dependencies

The Market Module must not depend on:

Brain Module
AI Runtime Module
Risk Module
Execution Module
Trade Lifecycle Module
Portfolio Module
Indicator Module
Responsibility

The Indicator Module provides technical analysis
information derived from market data.

The module is responsible for:

Indicator calculation
Indicator state generation
Technical measurement output

The Indicator Module does not:

Generate final trading decisions
Execute trades
Manage risk
Public Interface

Primary Interface:

IIndicatorProvider
Allowed Consumers

The following modules may consume Indicator interfaces:

Brain Module
AI Runtime Module
Allowed Dependencies

The Indicator Module may depend on:

Market Module
Data Module
Infrastructure Module
Forbidden Dependencies

The Indicator Module must not depend on:

Execution Module
Trade Lifecycle Module
Portfolio Module
Learning Module
Data Module
Responsibility

The Data Module provides data access and normalization
services required by other modules.

The module is responsible for:

Data retrieval
Data normalization
Data preparation

The Data Module does not:

Analyze market conditions
Generate signals
Execute trading actions
Public Interface

Primary Interface:

IDataProvider
Allowed Consumers

The following modules may consume Data interfaces:

Market Module
Indicator Module
Brain Module
Allowed Dependencies

The Data Module may depend on:

Infrastructure Module
Common Utilities
Forbidden Dependencies

The Data Module must not depend on:

Brain Module
AI Runtime Module
Risk Module
Execution Module
Trade Lifecycle Module
Portfolio Module

## Brain Module

### Responsibility

The Brain Module provides market reasoning
and contextual analysis for decision-making layers.

The module is responsible for:

- Market context analysis
- Structure interpretation
- Signal preparation
- Context generation

The Brain Module does not:

- Execute trades
- Manage risk
- Control positions
- Store learning models

---

### Public Interface

Primary Interfaces:

- IBrainProvider
- IBrainAnalyzer

---

### Allowed Consumers

The following modules may consume Brain interfaces:

- AI Runtime Module
- Risk Module

---

### Allowed Dependencies

The Brain Module may depend on:

- Market Module
- Indicator Module
- Data Module
- Common Utilities

---

### Forbidden Dependencies

The Brain Module must not depend on:

- Execution Module
- Position Module
- Trade Lifecycle Module
- Portfolio Module

---

## AI Runtime Module

### Responsibility

The AI Runtime Module provides AI-based
decision processing and intelligence execution.

The module is responsible for:

- Signal evaluation
- Decision scoring
- Confidence calculation
- Decision generation
- Strategy Setup candidate construction under an approved research contract
- Structure-aware Trade Plan proposal without Risk approval

The AI Runtime Module does not:

- Place orders directly
- Manage trade lifecycle
- Override risk controls

---

### Public Interface

Primary Interfaces:

- IAIDecisionProvider
- IAIInferenceProvider
- CHybridRuleSetupContext
- CTradeSetupCandidate
- CStructureAwareTradePlan
- CObjectiveMultiTimeframeSetupInput
- CObjectiveHybridSetupConfig
- CObjectiveMultiTimeframeSetupEvidence
- CObjectiveMultiTimeframeSetupAdapter
- CObjectiveSetupResearchProvider

---

### Allowed Consumers

The following modules may consume AI Runtime interfaces:

- Risk Module
- Execution Module

---

### Allowed Dependencies

The AI Runtime Module may depend on:

- Brain Module
- Market Module
- Indicator Module
- Data Module

---

### Forbidden Dependencies

The AI Runtime Module must not depend on:

- Execution Implementation
- Position Management Implementation
- Trade Lifecycle Implementation
- Portfolio Management Implementation

Strategy Setup and Trade Plan contracts must not:

- approve Risk;
- size a position;
- execute or mutate broker state;
- mix Feature, Label, Confidence, Risk, or Execution Result ownership;
- use future bars or live Dataset generation.

The CR-013 Stage B Objective adapter remains research-only and disconnected
from Runtime, Risk, Execution, and broker mutation until a separately approved
Stage C integration review is complete.

CR-013 Stage C is approved only for Strategy Tester. Runtime may consume
`CObjectiveSetupResearchProvider`, while the accepted AI plan must pass through
Decision and Risk before `CStructureAwareExecutionPlanAdapter` creates the
Execution-owned `CExecutionPricePlan`. Forward and broker consumers remain
forbidden.

---

## Risk Module

### Responsibility

The Risk Module provides risk evaluation
and protection controls before trade execution.

The module is responsible for:

- Risk validation
- Exposure evaluation
- Risk limit enforcement
- Trade approval decision

The Risk Module does not:

- Create trading signals
- Execute orders
- Manage positions directly

---

### Public Interface

Primary Interfaces:

- IRiskProvider
- IRiskValidator

---

### Allowed Consumers

The following modules may consume Risk interfaces:

- Execution Module
- Portfolio Module

---

### Allowed Dependencies

The Risk Module may depend on:

- AI Runtime Module
- Money Module
- Market Module
- Position Module

---

### Forbidden Dependencies

The Risk Module must not depend on:

- Execution Implementation
- Trade Lifecycle Implementation
- Learning Implementation

---

## Money Module

### Responsibility

The Money Module provides capital management
and position sizing calculation.

The module is responsible for:

- Position sizing
- Capital allocation
- Money calculation rules

The Money Module does not:

- Approve trades
- Execute orders
- Manage trade states

---

### Public Interface

Primary Interface:

- IMoneyManager

---

### Allowed Consumers

The following modules may consume Money interfaces:

- Risk Module
- Execution Module

---

### Allowed Dependencies

The Money Module may depend on:

- Portfolio Module
- Account Data
- Risk Configuration

---

### Forbidden Dependencies

The Money Module must not depend on:

- Brain Module
- AI Runtime Decision Logic
- Trade Lifecycle Implementation

---

## Execution Module

### Responsibility

The Execution Module converts approved
trade decisions into executable actions.

The module is responsible for:

- Order preparation
- Order validation
- Order submission
- Execution result reporting

The Execution Module does not:

- Generate signals
- Override risk decisions
- Learn strategies

---

### Public Interface

Primary Interface:

- IExecutionProvider
- CExecutionPricePlan

`CExecutionPricePlan` is an Execution-owned price contract. It contains no
Brain or AI implementation dependency. Runtime owns the approved Stage C
mapping after Risk evaluation; Execution may validate/reject but may not alter
the supplied structural Stop/Target.

---

### Allowed Consumers

The following modules may consume Execution interfaces:

- Trade Lifecycle Module

---

### Allowed Dependencies

The Execution Module may depend on:

- Risk Module
- Money Module
- Position Module
- Infrastructure Module

---

### Forbidden Dependencies

The Execution Module must not depend on:

- Brain Module
- AI Runtime Decision Logic
- Learning Module

---

## Position Module

### Responsibility

The Position Module provides position state
management and position information.

The module is responsible for:

- Position tracking
- Position status
- Position information access

The Position Module does not:

- Generate decisions
- Execute orders
- Manage strategy learning

---

### Public Interface

Primary Interface:

- IPositionProvider

---

### Allowed Consumers

The following modules may consume Position interfaces:

- Risk Module
- Execution Module
- Trade Lifecycle Module

---

### Allowed Dependencies

The Position Module may depend on:

- Execution Module
- Infrastructure Module

---

### Forbidden Dependencies

The Position Module must not depend on:

- Brain Module
- AI Runtime Module
- Learning Module

---

## Trade Lifecycle Module

### Responsibility

The Trade Lifecycle Module manages
the complete lifecycle of executed trades.

The module is responsible for:

- Trade state management
- Entry tracking
- Exit management
- Trade event handling

---

### Public Interface

Primary Interface:

- ITradeLifecycleProvider

---

### Allowed Consumers

The following modules may consume Trade Lifecycle interfaces:

- Portfolio Module
- Learning Module

---

### Allowed Dependencies

The Trade Lifecycle Module may depend on:

- Execution Module
- Position Module
- Risk Module

---

### Forbidden Dependencies

The Trade Lifecycle Module must not depend on:

- Brain Module
- AI Decision Logic

---

## Portfolio Module

### Responsibility

The Portfolio Module manages
account-level trade information.

The module is responsible for:

- Portfolio state
- Performance information
- Exposure summary

---

### Public Interface

Primary Interface:

- IPortfolioProvider

---

### Allowed Consumers

The following modules may consume Portfolio interfaces:

- Learning Module
- Risk Module

---

### Allowed Dependencies

The Portfolio Module may depend on:

- Position Module
- Trade Lifecycle Module

---

### Forbidden Dependencies

The Portfolio Module must not depend on:

- Brain Module
- Execution Decision Logic

---

## Learning Module

### Responsibility

The Learning Module provides
model improvement and adaptation capability.

The module is responsible for:

- Data collection
- Model evaluation
- Learning improvement

The Learning Module does not:

- Execute trades
- Override live risk controls

---

### Public Interface

Primary Interface:

- ILearningProvider

---

### Allowed Consumers

The following modules may consume Learning interfaces:

- AI Runtime Module

---

### Allowed Dependencies

The Learning Module may depend on:

- Portfolio Module
- Trade Lifecycle Module
- Market Module

---

### Forbidden Dependencies

The Learning Module must not depend on:

- Execution Module
- Order Management Logic

---

# Dependency Contract

All module dependencies must follow
the approved architecture direction.

The dependency model is:

```text
Source Layer
      ↓
Reasoning Layer
      ↓
Control Layer
      ↓
Action Layer
      ↓
Feedback Layer
Dependency Enforcement

Every module must:

Depend only on approved interfaces
Respect module ownership boundaries
Avoid direct implementation coupling
Maintain dependency direction

Any dependency outside this catalog
requires architecture review.

Interface Change Policy

Public interfaces are considered
architecture contracts.

Any change affecting:

Interface name
Interface responsibility
Input contract
Output contract
Dependency relationship

requires review before implementation.

Breaking Change Rules

A breaking interface change includes:

Removing an existing interface
Changing interface responsibility
Changing expected behavior
Moving ownership to another module

Breaking changes require:

Impact analysis
Architecture review
Documentation update
Approval before merge
Non-Breaking Change Rules

Non-breaking changes include:

Internal implementation updates
Performance improvements
Refactoring without contract changes

These changes must:

Preserve interface behavior
Preserve dependency rules
Maintain backward compatibility
Contract Violation Handling

If a module violates this catalog:

The violation must be:

Identified
Documented
Reviewed
Corrected before implementation continues

Examples of violations:

Cross-layer dependency
Interface bypass
Duplicate responsibility
Hidden coupling
Review Requirement

Before any new module implementation:

The following documents must be reviewed:

PROJECT_CONSTITUTION.md
ARCHITECTURE_PRINCIPLES.md
ARCHITECTURE_DECISIONS.md
ARCHITECTURE_FREEZE.md
MODULE_DEPENDENCY_RULES.md
MODULE_INTERFACE_CATALOG.md

Implementation must not start
when module boundaries are undefined.

Foundation Completion Criteria

MODULE_INTERFACE_CATALOG.md is considered complete when:

All major modules have defined contracts
Interfaces have clear ownership
Dependencies are documented
Forbidden dependencies are identified
Markdown validation passes
Document Review Status

Document:

MODULE_INTERFACE_CATALOG.md

Review Phase:

Phase 0.3 — Foundation Architecture Review

Review Status:

Completed

Architecture Baseline:

ABR-1.0

Document Ownership

Owner:

XAU AI PLATFORM Architecture Team

Document Type:

Architecture Contract Document

Maintained By:

Project Architecture Governance Process

Authority:

PROJECT_CONSTITUTION.md
ARCHITECTURE_PRINCIPLES.md
ARCHITECTURE_FREEZE.md
ARCHITECTURE_DECISIONS.md
Change History
Version Date    Change Description
1.0.0 Initial Initial module interface catalog created
1.1.0 Phase 0.3 Standardized module contracts and governance alignment

End of MODULE_INTERFACE_CATALOG
