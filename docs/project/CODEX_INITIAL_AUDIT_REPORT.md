# Architecture Baseline Audit Report

**Audit result:** Not conformant with ABR-1.0.

## Scope

Read-only review of 357 working-tree files (846,720 bytes). No files were modified during the audit.

## 1. Repository Structure

- The working tree contains 249 `core` files, 91 documentation files, 8 test files, 7 root files, and 2 VS Code settings files.
- The frozen structure requires `assets/` and `core/config/`, but neither exists. It does not document the existing `core/core/` directory; it documents `dashboard/`, while the actual directory is `Dashboard/`.
- `docs/FolderStructure.md` describes `core/utils/` and `experts/`; neither exists. The EA entry point is instead at repository root.
- Twenty-three source files are empty: all Backtest and Optimizer implementations are placeholders. Their unimplemented status is not consistently documented.
- The repository is entirely untracked according to Git status, including baseline documentation and source. The declared frozen baseline is therefore not reproducible or enforceable through version control.

## 2. Core Module Alignment

- There are three competing application paths:
  - Active EA path: `XAU-AI-PLATFORM.mq5 -> CCore -> CRuntimeManager`.
  - Alternate path: `CCoreEngine -> CAIApplication -> CSystemManager`.
  - Kernel path: `CKernel/CApplication/CModuleRegistry`.
- Only the first path is used by the EA; the other two are disconnected from production startup.
- `CCore::Tick()` does not pass its symbol/timeframe arguments to `CRuntimeManager::SetContext()`. `ProcessPipeline()` returns while `m_symbol` is empty, so the active EA pipeline cannot run.
- The active execution pipeline validates and assembles an `ExecutionResult`, but never invokes `CTradeManager` or `CTradeExecutor`. The MT5 `CTrade` execution path is orphaned from the active pipeline.
- `CBrainAnalyzer` performs risk approval and embeds `CRiskResult` in the Brain result. This violates the declared `Brain -> Decision -> Risk` boundary.
- `CExecution` starts a trade lifecycle and `CRuntimeManager` starts another lifecycle for the same result, duplicating ownership.
- Four class names are duplicated: `CAIEngine`, `CATRResult`, `CExecutionPipeline`, and `CModuleRegistry`.
- The interface catalog's documented contracts (`IMarketProvider`, `IIndicatorProvider`, `IDataProvider`, `IBrainProvider`, and related interfaces) are absent. Integration relies primarily on concrete classes.
- The functional tests are stale against current APIs; `TestMarket` also references a nonexistent include path.

## 3. Documentation Alignment

- Primary architecture documents define incompatible flows:
  - `docs/Architecture.md`: `Market -> Context -> Brain -> Score -> Signal -> Decision -> Risk -> Execution`.
  - `docs/project/DEPENDENCY_RULES.md`: `Runtime -> Market -> Context -> Brain -> Decision -> Risk -> Execution -> Trade Lifecycle -> Portfolio -> Learning`.
  - `docs/project/MODULE_INTERFACE_CATALOG.md`: `Market -> Brain -> AI Runtime -> Risk -> Execution -> Trade Lifecycle -> Portfolio -> Learning`.
- The roles of Context, Score, Signal, Decision, and AI Runtime are not reconciled.
- The architecture roadmap labels Risk, Execution, AI, Portfolio, and Optimization as planned, while code implementations or scaffolds already exist for each.
- The repository quality report requires no empty required documents, but root `CHANGELOG.md`, `ROADMAP.md`, `LICENSE.md`, and `docs/DecisionLog.md` are empty. Several Codex governance documents are also empty.
- Documentation calls ABR-1.0 frozen, while code remains untracked and contains unresolved includes, duplicate classes, and incompatible tests. The freeze claim is unsupported by repository evidence.

## 4. Dependency Direction

| Observed dependency | Baseline result |
| --- | --- |
| `brain -> risk` (`BrainAnalyzer`) | Violation: Brain must not manage risk; Risk follows Decision. |
| `brain -> engine` and `engine -> brain` | Cycle: Brain depends on `engine/models`, while Engine depends on Brain. |
| `decision/models -> risk/models` | Reverse dependency: Decision directly owns a risk result although Risk follows Decision. |
| `ai -> execution` (`DecisionExecutor`) | Violation: AI Runtime directly accesses Execution implementation rather than an approved contract. |
| `execution -> ai` and `execution -> trade` | Violation/cycle risk: Execution accepts AI decisions and owns Trade Lifecycle despite the documented downstream flow. |
| `trade -> execution` | Valid in isolation, but forms a cycle with `execution -> trade`. |
| `runtime -> brain/ai/risk/execution/trade` | Undocumented: Runtime directly owns domain implementations although its documented allowed dependencies are common/config/logging. |

The static module graph is cyclic and concrete-class based, contrary to the baseline's acyclic, public-contract-only requirement.

## 5. Potential Architecture Violations

### Critical

- Active EA processing is inert because `Tick()` discards market context.
- The approved execution path does not reach the MT5 trade executor.
- Brain performs risk approval, violating layer isolation.

### High

- Cycles exist between Brain/Engine and Execution/Trade.
- Production integration bypasses the documented interface catalog.
- Duplicate public class names can break compilation and create ambiguous ownership.
- Tests do not match current contracts.

### Medium

- Nine local source includes are unresolved:
  - `core/XAUBrain.mqh`
  - `core/decision/DecisionManager.mqh`
  - `core/position/PositionPipeline.mqh` (six includes)
  - `tests/TestMarket.mq5`
- `PositionPipeline.mqh` is an apparent copy of `ExecutionPipeline.mqh`, retaining its class name, include guard, purpose, and Execution dependencies.
- Architecture documentation has multiple competing sources of truth and stale folder/roadmap claims.

## Baseline Conclusion

ABR-1.0 is documented as frozen but is not reflected in implementation. The repository should be treated as an **in-progress architecture prototype**, not a baseline-conformant trading platform, until it has one canonical runtime path, contract-based module boundaries, an acyclic dependency graph, aligned documentation, and compilable tests.
