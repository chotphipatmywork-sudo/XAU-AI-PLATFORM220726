# XAU-AI-PLATFORM Architecture Compliance Audit — Round 2

Audit role: Architecture Compliance Auditor  
Scope: read-only source, folder, and include-dependency analysis  
Architecture baseline: ABR-1.0

## Finding 1

Finding: Production entry bypasses Kernel.

Location: `XAU-AI-PLATFORM.mq5:10`; `core/Core.mqh:13`

Severity: A

Category: Architecture Breaking

Reason: The sole EA entry includes and instantiates `CCore`, which directly owns `CRuntimeManager`. `CKernel` is not reached. This violates the mandatory `Entry → Kernel → Runtime` prefix.

Architecture Reference: `docs/Architecture.md` §§1–4; ADR-001 “Decision” and “Runtime Ownership”.

Recommended Correction: Make the EA entry instantiate/use `CKernel`; make Kernel own the one Runtime implementation. Retire or isolate `CCore` as non-production infrastructure.

## Finding 2

Finding: The production runtime does not propagate tick context and omits required canonical stages.

Location: `core/Core.mqh:45`; `core/runtime/RuntimeManager.mqh:166`

Severity: A

Category: Architecture Breaking

Reason: `CCore.Tick(symbol,timeframe)` ignores both arguments; `CRuntimeManager.SetContext()` is never called. Because `ProcessPipeline()` exits when `m_symbol == ""`, the production tick path cannot reach Brain or subsequent stages. Additionally, Runtime directly coordinates Brain → AI → Risk → Execution; Market, Decision, Portfolio, and Learning are not wired into the production flow.

Architecture Reference: `docs/Architecture.md` §§1, 4–6; ADR-001 “Validation Criteria”.

Recommended Correction: Route symbol/timeframe through Runtime, then explicitly orchestrate every canonical stage in order.

## Finding 3

Finding: Brain owns Risk analysis, approval data, and `RiskResult`.

Location: `core/brain/BrainAnalyzer.mqh:18`; `core/brain/models/BrainAnalysisResult.mqh:17`

Severity: B

Category: Boundary Violation

Reason: `CBrainAnalyzer` instantiates `CRiskAnalyzer`, calls `AllowTrading()`, and populates `CRiskResult` fields including approval, risk level, score, and recommended risk. The Brain output model also contains `CRiskResult`.

Architecture Reference: ADR-003 “Brain Responsibility” and “Risk Responsibility”; `docs/Architecture.md` §6.2.

Recommended Correction: Remove Risk types and risk evaluation from Brain. Brain should emit only market context/signal/proposal; Risk should evaluate the resulting decision independently.

## Finding 4

Finding: Decision is coupled to, and gates on, Risk before the required Risk stage.

Location: `core/decision/models/DecisionContext.mqh:17`; `core/decision/engines/DecisionEngine.mqh:40`

Severity: C

Category: Dependency Violation

Reason: Decision includes and consumes `RiskResult`, then prevents decision creation based on `Risk.AllowTrade`. This reverses the approved responsibility order: Decision expresses intent; Risk determines permission afterwards.

Architecture Reference: ADR-002 “Approved Module Dependency Flow” and “Decision Layer”; ADR-003 “Decision Responsibility”.

Recommended Correction: Remove `RiskResult` from `DecisionContext` and run Risk only after `DecisionResult` has been produced.

## Finding 5

Finding: Execution pipeline stops at `ExecutionResult`; `TradeExecutor` is unreachable from the active execution chain.

Location: `core/execution/ExecutionPipeline.mqh:191`; `core/execution/TradeManager.mqh:69`

Severity: A

Category: Architecture Breaking

Reason: `ExecutionPipeline` builds and assembles an `ExecutionResult` but never creates or calls `CTradeManager`/`CTradeExecutor`. `TradeExecutor` contains the only buy/sell broker calls, yet is disconnected from `ExecutionManager → ExecutionPipeline`.

Architecture Reference: ADR-004 “Execution Pipeline Ownership” and “Validation Criteria”; `docs/Architecture.md` §6.6.

Recommended Correction: Make the pipeline invoke `TradeManager`, which invokes `TradeExecutor`, after validation and request construction; return the broker-derived result.

## Finding 6

Finding: Risk approval and position sizing are not enforced as a Risk-owned execution input.

Location: `core/runtime/RuntimeManager.mqh:101`; `core/execution/builder/ExecutionContextBuilder.mqh:23`; `core/execution/TradeRequestBuilder.mqh:18`

Severity: B

Category: Boundary Violation

Reason: Runtime performs only a Boolean `AllowTrading()` check, then passes a raw `CAIDecision` to Execution. No approved Risk result, risk constraints, exposure outcome, or Risk-calculated position size is carried into Execution. Execution supplies a default `0.01` lot itself.

Architecture Reference: ADR-003 “Risk Responsibility” and “Execution Boundary”; ADR-004 “Risk Enforcement Rule”.

Recommended Correction: Define a Risk-approved decision/request containing approval, calculated size, and constraints. Execution must accept only that type and must not supply sizing defaults.

## Finding 7

Finding: Trade Lifecycle has duplicate ownership and is started twice for one execution result.

Location: `core/execution/Execution.mqh:94`; `core/runtime/RuntimeManager.mqh:150`

Severity: B

Category: Boundary Violation

Reason: Both `CExecution` and `CRuntimeManager` own a `CTradeLifecycle` and call `StartFromExecution()` after the same execution. This creates duplicate lifecycle state ownership.

Architecture Reference: ADR-004 “Trade Lifecycle Boundary”; `docs/Architecture.md` §6.7.

Recommended Correction: Assign one handoff owner. Execution should emit a successful execution event/result; the single Trade Lifecycle module should consume it once.

## Finding 8

Finding: Alternative application/execution routes remain and include a Risk-bypassing path.

Location: `core/engine/AIEngine.mqh:11`; `core/application/AIApplication.mqh:13`; `core/core/CoreEngine.mqh:13`

Severity: A

Category: Architecture Breaking

Reason: `CAIEngine` performs Brain → DecisionAdapter → DecisionExecutor/Execution with no Risk stage. `CAIApplication`, `CCoreEngine`, `CApp`, `CSystemController`, and `CSystemManager` also duplicate runtime/lifecycle controller roles. Several are currently incomplete, but their presence preserves contradictory runtime designs prohibited by the ADR.

Architecture Reference: ADR-001 “Rejected Runtime Paths”; ADR-003 “Execution Boundary”; ADR-004 “Risk Enforcement Rule”.

Recommended Correction: Remove or quarantine legacy controllers from production compilation, and converge all supported runtime behavior behind Kernel and the canonical pipeline.

## Finding 9

Finding: Folder/module structure contains duplicate ownership artifacts.

Location: `core/kernel/ModuleRegistry.mqh:12`; `core/application/ModuleRegistry.mqh:31`; `core/position/PositionPipeline.mqh:1`

Severity: D

Category: Documentation / Minor

Reason: Two unrelated `CModuleRegistry` definitions exist, and `position/PositionPipeline.mqh` duplicates the execution pipeline’s implementation and identity. This conflicts with the documented module ownership model and makes future dependency control unreliable.

Architecture Reference: `docs/Architecture.md` §§3, 7; ADR-002 “Dependency Ownership Rule”.

Recommended Correction: Retain one registry under Kernel and remove or rename obsolete duplicate pipeline artifacts after confirming they have no supported callers.

## Final Summary

- Confirmed direct include cycle: none in the production entry include closure.
- Canonical runtime path: failed.
- Dependency direction: failed due to Brain/Decision dependencies on Risk.
- Brain/Risk boundary: failed.
- Execution ownership/completeness: failed.
- Source/folder responsibilities: inconsistent with `Architecture.md` and ADRs.

Architecture Compliance Status: **FAIL**

Architecture Freeze Recommendation: **NOT READY**
