# IMP-021 Feature Projection Correction

Status: Implemented; pending MetaEditor compilation validation.

Candidate diagnostics showed that the schema 1.0.0 dataset had constant Trend and Session values: Trend strength did not retain bullish/bearish direction, while Session confidence was always `1.0`. This left the trainer with little usable variation.

Schema 1.1.0 retains the four canonical feature groups while correcting their representation:

- Trend: signed directional strength on a 0..100 scale with neutral 50.
- Volatility: ATR ratio confidence scaled from its natural near-1 range to the canonical 0..100 range.
- Liquidity: unchanged score.
- Session: Asia/London/New York encoded as 25/50/75.

This is a dataset and model-contract compatibility change. All schema 1.0.0 CSV partitions and baseline artifacts are deprecated. Regenerate, validate, split, and re-train before any future evaluation. The focused test is `tests/TestBrainFeatureAdapter.mq5`.
