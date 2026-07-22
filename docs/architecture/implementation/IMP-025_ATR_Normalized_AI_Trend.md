# IMP-025 ATR-Normalized AI Trend Score

Status: Implemented; pending MetaEditor compilation validation.

The 6,679-record Feature Schema 1.1.0 diagnostic found that Trend had only three distinct values and a Validation permutation macro-F1 drop of `0.0025`. Schema 1.3.0 therefore adds `CTrendResult.AITrendScore` for the AI feature path.

`CTrendAnalyzer` obtains ATR(14) through its existing indicator provider. `CTrendAssembler` calculates the new score from EMA separation and EMA slope divided by ATR, caps the components, reduces strength when slope disagrees with the EMA direction or CHOCH is present, and maps the signed result around neutral 50. The score is clamped to 0..100.

`Trend.Strength`, `Trend.Direction`, and `Trend.Confidence` remain unchanged. Decision continues to consume `Trend.Strength`; only `CBrainFeatureAdapter` consumes `AITrendScore`. The four canonical feature groups and their CSV order remain unchanged.

All Schema 1.1.0 CSV partitions and preliminary artifacts are incompatible with Schema 1.3.0. Focused validation EAs are `tests/TestAITrendScore.mq5` and `tests/TestBrainFeatureAdapter.mq5`.
