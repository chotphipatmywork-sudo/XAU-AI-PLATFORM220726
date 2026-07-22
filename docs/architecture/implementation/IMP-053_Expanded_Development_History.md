# IMP-053 Expanded Development History

Status: Completed; expanded development history evaluated, deployment gate failed.

## Reason

Schema 4.0 and all bounded Train-only feature/model investigations failed the stable deployment gate. The current Train partition contains only 4,656 M15 records from a limited set of market regimes. Continuing to add candidates or thresholds after inspecting the same folds would create selection bias.

The next controlled development step increases historical regime coverage without changing Feature Schema 4.0, Label Schema 1.1, Brain ownership, or the Runtime path.

## Generation plan

Run the existing one-shot `TestHistoricalDatasetOrchestrator` with:

- `DatasetBars=40000`
- `ReplaceExistingDataset=true`
- `ProgressInterval=100`
- unchanged M15, 16-bar, +/-1.5 ATR(14) labeling

`DatasetBars` defines a calendar-duration request, so weekends and unavailable broker bars mean fewer than 40,000 records will be returned. Based on the current rate, approximately 26,000–28,000 market bars and five to six hours of generation are expected; actual broker history controls the result.

After generation, rerun Validator, purged Splitter, Partition Validator, and Readiness Gate. No Python training may start until all four pass. H1 research export is not required because CR-002 was rejected.

## Evidence preservation

Before regeneration, the current Dataset, Train, Validation, Test, and H1 auxiliary files were copied to `training/output/evidence_20260716_schema4/` with line counts, byte sizes, and SHA-256 hashes recorded in its manifest.

## Completed generation and validation

The one-shot MT5 generation completed on 2026-07-16:

- requested calendar bars: `40,000`
- available M15 market bars processed: `27,008`
- Dataset records written: `26,864`
- Dataset period: `2025-05-26 01:00:00` through `2026-07-16 06:30:00`
- labels BUY/HOLD/SELL: `11,804 / 2,938 / 12,122`
- duplicate IDs/timestamps: `0 / 0`
- invalid features/labels: `0 / 0`

The purged chronological split produced:

- Train: `18,788`
- Validation: `4,013`
- Test: `4,031`
- removed at partition boundaries: `32` records (`16` per boundary)

Partition validation confirmed valid temporal order, valid label-horizon purges, complete label coverage, and no invalid or duplicate records. The Readiness Gate passed with `26,832` usable partition records.

## Expanded Train-only nested result

The registered nested purged Walk-forward method was rerun using only the expanded Train partition. Validation and Test were not read. The method used four Outer folds, three Inner folds, and the fixed 16-bar purge.

| Metric | Expanded Nested Outer | Required | Passed |
| --- | ---: | ---: | --- |
| Accuracy | 0.3376 | 0.45 | No |
| Macro F1 | 0.3337 | 0.40 | No |
| SELL precision | 0.4762 | 0.50 | No |
| SELL recall | 0.2854 | 0.30 | No |
| BUY precision | 0.4898 | 0.50 | No |
| BUY recall | 0.2948 | 0.30 | No |

No Outer fold passed the complete evaluation contract. Fold 2 collapsed to Accuracy `0.1759`, Macro F1 `0.1507`, SELL recall `0.0544`, and BUY recall `0.0628`. The selected probability variant, policy, and model also changed across the Outer histories.

The full-Train Inner selection chose a raw `random_forest_depth_10_balanced` model with argmax, but it also failed its aggregate gate and passed `0/3` Inner folds. Its locked Python artifact remains development-only and its paired policy keeps `deployment_authorized=false`.

Artifacts are stored under `training/output/expanded_20260716/`. The nested report SHA-256 is `3E71B22351FFF81E4CDCCF1D8A7CBFB4A6930944F13F4EF5C9D8093E1BE95FE6`.

The registered Temporal Regime Diagnostic confirmed that Trend Regime, Momentum, and Slope were the three largest distribution shifts. Fold 2 calibration converted near-balanced mean SELL/BUY probabilities into `88.84%` HOLD decisions. A raw-probability counterfactual recovered Macro F1 from `0.1507` to `0.3898` but still failed BUY recall and the complete gate. Calibration removal is therefore not sufficient evidence for another candidate run.

The controlled History Strategy comparison ranked rolling 1,000 records first with Macro F1 `0.4158`, SELL precision `0.4711`, and BUY precision `0.4847`. All seven expanding, rolling, and recency strategies passed `0/4` complete gates, so the result does not authorize replacing the registered training method.

Feature-Label Stability ranked Session first and Trend Regime second. Trend Regime changed directional sign across the four periods, while Session Progress retained a positive high-minus-low BUY relationship in `4/4` periods. This supports retaining Schema 4.0 but does not justify a static Session rule or deployment.

## Evaluation boundary

The expanded data is development evidence. Research decisions have already observed periods through 2026-07-16, so no period at or before that date can serve as genuinely fresh final deployment evidence. A method that passes expanded Train-only nested evaluation must be frozen, then evaluated once on a later untouched period collected after 2026-07-16.

The expanded Train-only method did not pass, so Validation and Test remain protected and unread. This result does not authorize Shadow or live deployment.
