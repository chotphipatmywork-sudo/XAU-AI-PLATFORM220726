# Model Training and Deployment Gate Review

Version: 1.1.0

Date: 2026-07-16

Architecture Baseline: ABR-1.0

Status: Phase evaluation closed; deployment NO-GO

## Scope

This review closes the current Feature Schema 4.0 training experiment and decides whether its locked candidate may enter non-trading Shadow Deployment. It does not authorize live orders and does not change the canonical Runtime path.

## Verified input

- XAUUSD M15 historical replay completed: 6,675 records.
- Dataset validation passed with no duplicate IDs, duplicate timestamps, invalid features, or invalid labels.
- Temporal split produced 4,656 Train, 985 Validation, and 1,002 Test records.
- Two 16-record boundary purges removed 32 records.
- Partition, label-horizon purge, and Readiness Gate passed.
- Feature Schema is `4.0.0`; Label Schema is `1.1.0`.

## Train-only method evidence

The ordinary four-fold purged Walk-forward selection produced Accuracy `0.4549` and Macro F1 `0.4236`, but no fold passed the complete contract.

The Schema 4.0 controlled ablation selected Session Progress before three of four Outer periods and from the complete Train history. Session Progress remains in the approved feature contract, but the ablation passed no complete Outer fold.

The complete Nested Purged Walk-forward process used four Outer folds, three Inner folds, raw and chronological probability variants, the bounded candidate grid, asymmetric decision policies, and a 16-record purge at every boundary. Validation and Test were not read.

| Metric | Nested Outer | Required | Passed |
| --- | ---: | ---: | --- |
| Accuracy | 0.4175 | 0.45 | No |
| Macro F1 | 0.3405 | 0.40 | No |
| SELL precision | 0.4993 | 0.50 | No |
| SELL recall | 0.6526 | 0.30 | Yes |
| BUY precision | 0.3636 | 0.50 | No |
| BUY recall | 0.1171 | 0.30 | No |

No Outer fold passed the complete evaluation contract. Selected models and policies changed across every Outer history. BUY recall collapsed in multiple unseen periods, demonstrating that the selection method is not temporally stable.

## Gate decision

`EligibleForShadowDeployment=false`.

The locked joblib and policy files are development artifacts only. Their policy metadata keeps `deployment_authorized=false`. They must not be exported to ONNX, loaded by MQL5, connected to AI Decision, or used to place orders.

Validation and Test remain untouched because the Train-only method failed before the unbiased evaluation stage. Reading them now would not rescue the rejected method and would consume protected evaluation evidence.

## Expanded-history confirmation

IMP-053 expanded the unchanged Feature Schema 4.0 development history from 6,675 to 26,864 Dataset records. Dataset validation, the 16-bar purged chronological split, Partition validation, and the Readiness Gate all passed. The new Train partition contains 18,788 records; Validation contains 4,013 and Test contains 4,031.

The same registered Train-only nested process was rerun without reading Validation or Test. Its expanded Outer estimate was:

| Metric | Expanded Nested Outer | Required | Passed |
| --- | ---: | ---: | --- |
| Accuracy | 0.3376 | 0.45 | No |
| Macro F1 | 0.3337 | 0.40 | No |
| SELL precision | 0.4762 | 0.50 | No |
| SELL recall | 0.2854 | 0.30 | No |
| BUY precision | 0.4898 | 0.50 | No |
| BUY recall | 0.2948 | 0.30 | No |

No Outer fold passed the complete contract. The wider market history therefore confirms the NO-GO decision instead of providing deployment evidence. The generated Python model remains locked as a development artifact with `deployment_authorized=false`.

The complete Phase decision and reopen conditions are recorded in `PHASE_7_MODEL_TRAINING_DEPLOYMENT_CLOSURE.md`.

## 2026-07-18 parity-corrected Train-only evidence

IMP-064 and IMP-067 corrected the full label horizon and Historical/Runtime
Session observation parity. The regenerated Dataset contains 26,850 records;
its purged Train/Validation/Test partitions contain 18,779/4,011/4,028 rows.
All content, temporal, purge, partition, and Readiness gates passed.

The registered four-fold Train-only selector was rerun with a sixteen-bar purge
without reading Validation or Test. It selected
`random_forest_depth_10_hold_2`, raw probabilities, and confidence threshold
0.35.

| Metric | Parity-corrected Train folds | Required | Passed |
| --- | ---: | ---: | --- |
| Accuracy | 0.4405 | 0.45 | No |
| Macro F1 | 0.4228 | 0.40 | Yes |
| SELL precision | 0.4555 | 0.50 | No |
| SELL recall | 0.3942 | 0.30 | Yes |
| BUY precision | 0.4749 | 0.50 | No |
| BUY recall | 0.4823 | 0.30 | Yes |

The aggregate contract failed, zero of four folds passed the complete contract,
and the stable Walk-forward gate failed. The locked artifact remains a
development-only NO-GO artifact. Validation, Test, MQL5 model integration, and
deployment remain unauthorized.

The Train-only permutation diagnostic ranked Session Context first for both
Macro F1 and BUY precision, followed by Volatility and Liquidity fields. Trend
Regime, Momentum, and Slope ranked lowest. This is association evidence for
future bounded Hybrid research, not permission to tune on protected data or to
change the canonical Feature Schema.

## Phase status

Training infrastructure, schema validation, purged splitting, candidate selection, diagnostics, and safe rejection behavior are implemented. Model Deployment cannot be completed under the current approved Feature/Label Contract because the quality gate is not met.

Further progress requires a separately approved research/change request that adds credible past-only market information inside the canonical Trend, Volatility, Liquidity, or Session groups, followed by complete dataset regeneration and a fresh evaluation cycle. Threshold retuning and adding candidates after inspecting these Outer periods are rejected as selection bias.

## Preserved boundaries

- Brain remains market understanding only.
- Live inference remains separate from offline training.
- Risk remains the final permission gate.
- Execution and Trade Lifecycle are unchanged.
- No model is deployed and no live-trading authorization is granted.
