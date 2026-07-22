# IMP-045 Feature Contract 4.0 Session Progress Implementation

Status: Implemented and validated; model deployment gate closed.

IMP-067 later corrected Historical/Runtime Session observation-time parity.
Feature Schema remains `4.0.0`; Dataset rows generated before that correction
are not eligible for new model training.

## Approved change

CR-001 adds one field to the canonical Session group and appends it as feature 12:

```text
session_progress = 100 * elapsed minutes inside the active eight-hour session / 480
```

The complete Feature Schema 4.0 order is:

1. `trend_regime`
2. `trend_momentum`
3. `trend_slope`
4. `volatility_regime`
5. `volatility_change`
6. `liquidity_activity`
7. `liquidity_range_position`
8. `liquidity_sweep_direction`
9. `session_asia`
10. `session_london`
11. `session_new_york`
12. `session_progress`

Label Schema remains `1.1.0`: M15, 16 bars, and +/-1.5 ATR(14).

## Runtime implementation

- `CSessionEngine` calculates Progress from the current context timestamp after resolving the same 00:00/08:00/16:00 session boundaries.
- `CSessionResult` owns the new market-context value.
- `CBrainFeatureAdapter` clamps and projects it into `CAIFeatureVector`.
- Extractor and Normalizer carry the twelfth value without changing existing feature meanings.
- Placeholder inference retains its previous score formula and does not consume Session Progress.
- Decision, Risk, Execution, and Trade Lifecycle are unchanged.

## Dataset and training contract

- Writer appends `session_progress` immediately before `label`.
- Reader requires and reads 16 total CSV columns.
- Dataset validators require Session Progress within `0..100`.
- Model Training Contract and Python metadata report Feature Schema `4.0.0` with 12 features.
- Strict Python input rejects Schema 3.0 CSV headers.
- Walk-forward Session permutation treats the three one-hot values and Progress as one canonical group.

## Focused tests

New tests:

- `tests/TestSessionFeatureProgress.mq5`
- `training/test_feature_schema_contract.py`

Updated tests cover Brain projection, model contract, dataset feature construction, historical builder, and orchestration schema output.

## Local validation

MetaEditor CLI compiled all of the following with `0 errors / 0 warnings`:

- `TestSessionFeatureProgress.mq5`
- `TestBrainFeatureAdapter.mq5`
- `TestModelTrainingContract.mq5`
- `TestDataset.mq5`
- `TestHistoricalDatasetBuilder.mq5`
- `TestHistoricalBrainReplay.mq5`
- `TestHistoricalDatasetOrchestrator.mq5`
- `TestDatasetValidator.mq5`
- `TestDatasetSplitter.mq5`
- `TestDatasetPartitionValidator.mq5`
- `TestDatasetReadinessGate.mq5`
- `TestCompile.mq5`

Python schema, Session, feature diagnostic, confidence, walk-forward, nested purge, and syntax tests passed locally.

## Compatibility and next validation

Schema 3.0 datasets and model artifacts are incompatible and must not be used by the Schema 4.0 training pipeline. Before regeneration, copy the updated `core` and `tests` directories into the MT5 project copy and run `TestSessionFeatureProgress` on an XAUUSD M15 chart. The expected message is:

```text
Session feature progress valid: true
```

The MT5 runtime check passed on XAUUSD M15 at `2026.07.15 14:44:40.784` with `Session feature progress valid: true`.

Brain projection passed on XAUUSD M15 at `2026.07.15 14:48:27.213`. The adapter produced all 12 fields, ended with Session values `0.0/100.0/0.0/25.0`, and reported `Brain feature projection valid: true`.

Model Training Contract runtime validation passed at `2026.07.15 14:48:58.084`: contract and Feature Schema `4.0.0`, Label Schema `1.1.0`, 12 ordered inputs ending in `session_progress`, canonical SELL/HOLD/BUY mapping, and probability validation all matched the approved contract.

Schema 4.0 historical dataset regeneration started on XAUUSD M15 at `2026.07.15 14:50:34.547` with 10,000 requested bars, replace mode, Feature Schema `4.0.0`, and the unchanged Label Schema `1.1.0` configuration.

Generation completed at `2026.07.15 16:17:10.697`: all `6,690/6,690` available bars were processed and `6,679` Schema 4.0 records were written. No abnormal termination was reported. Dataset content validation remains pending.

At `21:07:41.879`, the still-attached test restarted after MT5/chart reinitialization and replaced the completed file. Attaching Validator terminated that second run at 2,709 rows. The partial file is rejected for training. IMP-046 adds one-shot self-removal and requires complete regeneration.

The recovery generation completed at `2026.07.16 07:07:04.032`: all `6,686/6,686` available bars were processed, `6,675` records were written, and the one-shot test called `ExpertRemove()`.

Validator, purged Splitter, Partition Validator, and Readiness Gate all passed. The final partitions contain 4,656 Train, 985 Validation, and 1,002 Test rows after 32 boundary records were purged. The Schema 4.0 Train-only controlled ablation retained Session Progress, but the complete nested model-selection process passed no Outer fold. Deployment remains unauthorized; see `MODEL_TRAINING_DEPLOYMENT_GATE_REVIEW.md`.
