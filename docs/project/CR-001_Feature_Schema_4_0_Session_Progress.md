# CR-001 Proposed Feature Schema 4.0 Session Progress

Version: 1.0.1

Date: 2026-07-15

Status: Implemented and evaluated; Feature retained, deployment gate closed

Architecture Baseline: ABR-1.0

Related Phase: Phase 7 — Model Training and Deployment

Priority: Controlled improvement

Requester: XAU AI PLATFORM project owner with Codex analysis support

## Problem statement

Feature Schema 3.0 has weak local label separation and no stable confidence-only deployment region. Static and past-only Trend extensions failed nested confirmation. Session has measurable label association, but the current three one-hot values identify only the active session and discard its internal phase.

## Current design

The Session Brain result exposes `State`, `Tradable`, and runtime `Confidence`. The AI tensor contains only `session_asia`, `session_london`, and `session_new_york`. Historical rows already store the bar timestamp, and Session boundaries are fixed at 00:00, 08:00, and 16:00 platform time.

## Proposed change

Append one bounded field to the canonical Session feature group:

12. `session_progress`

Encoding:

```text
100 * elapsed minutes within the active eight-hour session / 480
```

The proposed public Feature Schema identifier is `4.0.0`, subject to architecture and version approval. Label Schema remains `1.1.0`. The existing eleven fields retain their order and meaning.

## Evidence

IMP-043 controlled comparison improved aggregate Macro F1 from `0.3939` to `0.4005` and BUY precision from `0.4066` to `0.4221`.

IMP-044 nested selection chose Session Progress in `3/4` histories and improved the mixed Outer estimate to Accuracy `0.4142`, Macro F1 `0.3976`, BUY precision `0.4174`, and BUY recall `0.3754`. No Outer fold passed the complete deployment gate.

## Expected benefits

- Preserve all four canonical feature groups.
- Add missing intra-session market context without price or label leakage.
- Use the same deterministic encoding in live Brain output and historical replay.
- Avoid further derivatives of unstable Trend snapshots.
- Add only one tensor dimension and no external dependency.

## Architecture boundaries

- Canonical flow remains `Market -> Brain -> AI Runtime -> Decision -> Risk -> Execution -> Trade Lifecycle`.
- Session remains owned by Brain and consumes only the current market timestamp.
- AI receives market context only; no Risk, execution, confidence target, or trade result enters the feature tensor.
- Live inference remains independent from offline dataset generation and training.
- Label Schema `1.1.0` remains M15, 16 bars, and +/-1.5 ATR(14).
- No folder, module ownership, or dependency direction changes are proposed.

## Interface classification

This is a breaking shared data-contract change for strict CSV readers, feature vectors, model metadata, and existing model artifacts. It requires Architecture Review and a proposed MAJOR Feature Schema increment. It is not a change to the ABR-1.0 runtime boundary.

## Affected implementation

If approved, the implementation is limited to:

- `core/brain/session/models/SessionResult.mqh`
- `core/brain/session/engines/SessionEngine.mqh`
- `core/ai/features/FeatureExtractor.mqh`
- `core/ai/features/FeatureNormalizer.mqh`
- `core/ai/AITrainingEngine.mqh`
- `core/ai/BrainFeatureAdapter.mqh`
- `core/ai/DatasetValidator.mqh`
- `core/ai/DatasetPartitionValidator.mqh`
- `core/ai/storage/DatasetWriter.mqh`
- `core/ai/storage/DatasetReader.mqh`
- `core/ai/models/ModelTrainingContract.mqh`
- compatible Python schema readers and focused tests
- applicable architecture and training documentation

The placeholder inference score may ignore the new field until a separately approved deployed model consumes the 12-value tensor; its existing runtime behavior must not change accidentally.

## Compatibility and migration

- Schema 3.0 CSV partitions and model artifacts become incompatible with strict Schema 4.0 readers.
- Dataset files must be regenerated with replace mode after implementation.
- Validator, Splitter, Partition Validator, and Readiness Gate must pass before training.
- All candidate selection must restart from regenerated Train data.
- Existing Validation/Test results cannot be represented as Schema 4.0 evidence.
- No Schema 4.0 artifact is deployable until a newly dated untouched evaluation period passes the approved model gate.

## Required validation

1. Add a focused `TestSessionFeatureProgress.mq5` covering boundaries and M15 intra-session values.
2. Update and compile Brain adapter, model contract, historical orchestration, dataset validator, partition validator, historical replay, and compile-smoke tests.
3. Require `0 errors / 0 warnings` for every affected MetaEditor test.
4. Run Python focused Session, nested, schema, and walk-forward tests.
5. Regenerate the historical dataset, validate, purge/split, and run Train-only selection.
6. Keep the deployment gate closed unless later unbiased evaluation passes.

## Risks

- The improvement is modest and all current Outer folds still fail the complete gate.
- Platform-time session boundaries may differ from actual market microstructure or daylight-saving behavior.
- A random forest may exploit time correlations that do not persist in a later period.
- Regeneration and model retraining are mandatory.

## Alternatives considered

- More Trend interactions or history: rejected by IMP-038 and IMP-040.
- Additional confidence thresholds: rejected by IMP-042.
- CHOCH/BOS exposure: rejected for this request because current CHOCH is a placeholder and BOS does not yet represent a true historical break event.
- Multi-timeframe context: deferred because it is materially larger and requires new replay/data dependencies.
- No change: safest fallback if CR-001 is rejected.

## Rollback plan

Revert only CR-001 implementation files to Schema 3.0, restore the eleven-column CSV contract and `3.0.0` metadata, discard all Schema 4.0 datasets/artifacts, and regenerate Schema 3.0 partitions if further work is required. Runtime Decision, Risk, Execution, and Trade Lifecycle require no rollback because this proposal does not change them.

## Approval record

- Architecture Review: Approved by project owner on 2026-07-15
- Interface Review: Approved for the bounded CR-001 scope
- Version Review: Feature Schema `4.0.0` approved
- Implementation approval: Approved by project owner on 2026-07-15
- Deployment approval: Not requested

## Implementation record

- Workspace implementation completed: 2026-07-15
- Local MetaEditor compile: 12 affected tests, `0 errors / 0 warnings`
- Python focused validation: Passed
- MT5 runtime test: Passed on XAUUSD M15 (`2026.07.15 14:44:40.784`)
- MT5 Brain feature projection: Passed with 12 fields (`2026.07.15 14:48:27.213`)
- MT5 Model Training Contract: Passed for Feature Schema `4.0.0` / Label Schema `1.1.0` (`2026.07.15 14:48:58.084`)
- Schema 4.0 dataset regeneration and validation: Passed on 2026-07-16
- Schema 4.0 dataset generation started: XAUUSD M15, 10,000 requested bars (`2026.07.15 14:50:34.547`)
- Schema 4.0 dataset generation completed: `6,679` records from `6,690` available bars (`2026.07.15 16:17:10.697`)
- Dataset recovery required: attached test restarted at `21:07:41.879` and was terminated at 2,709 rows; IMP-046 one-shot safety fix implemented
- Recovery generation completed: `6,675` records from `6,686` available bars; one-shot `ExpertRemove()` confirmed (`2026.07.16 07:07:04.032`)
- Dataset validation: Passed; BUY/HOLD/SELL `2,702/719/3,254`, duplicates `0`, invalid features/labels `0`
- Purged split: TRAIN/VALIDATION/TEST `4,656/985/1,002`; 32 boundary records purged
- Partition and Readiness Gates: Passed; training-ready records `6,643`
- Schema 4.0 controlled ablation: Session Progress selected in `3/4` Outer histories and on complete Train; no Outer fold passed the complete model gate
- Schema 4.0 nested model selection: Failed deployment gate; Validation and Test remain unread
- Closure status: CR-001 implementation closed; model deployment remains unauthorized

## 2026-07-18 parity correction

IMP-067 corrected an implementation mismatch without changing the approved
Feature Schema. Runtime already evaluated Session at the completed-bar
observation timestamp, while Historical Brain Replay used the bar-open
timestamp. Both paths now use the shared `CClosedBarObservationTime` resolver.

The 26,900-row Dataset generated before this correction is retained only as
full-label-horizon and structural-validation evidence. It is not eligible for
new model training. A new Dataset and all downstream Dataset gates are required
after the parity test and MetaEditor compile pass.

The IMP-067 five-target MetaEditor compile passed on 2026-07-18 with
`0 errors / 0 warnings`, authorizing the focused MT5 runtime parity check.

Focused runtime parity validation then passed on XAUUSD M15 at
`2026.07.18 16:13:06.035`: observation timestamp, Session boundary, Session
progress, and the complete parity contract all reported `true`. Corrected
Dataset regeneration is now authorized; model training remains unauthorized
until all downstream Dataset gates pass.

The corrected XAUUSD M15 Dataset regeneration completed at
`2026.07.18 22:04:19.125` with 26,850 records and a confirmed one-shot
`ExpertRemove()`. Dataset content validation remains pending.

Content validation passed at `2026.07.18 22:11:40.910`: BUY/HOLD/SELL were
11,797/2,948/12,105; all duplicate and invalid counters were zero; Dataset
validity was `true`. Purged chronological splitting remains the next gate.

Purged splitting passed at `2026.07.18 22:17:00.897`: partitions contain
18,779/4,011/4,028 Train/Validation/Test rows, 32 boundary rows were purged,
and split validity was `true`. Cross-partition validation is the next gate.

Cross-partition validation passed at `2026.07.18 22:19:16.715`: all label
classes are represented in each partition, duplicate/invalid counters are zero,
temporal ordering is valid, both purge gaps are 15,300 seconds, and partition
Dataset validity is `true`. Readiness evaluation is the final Dataset gate.

Readiness passed at `2026.07.18 22:21:46.214`: 26,818 purged records are
available, partition validity, size, label coverage, and final training
readiness all reported `true`. The parity correction evidence is closed;
controlled Train-only model research is authorized while deployment and live
execution remain NO-GO.
