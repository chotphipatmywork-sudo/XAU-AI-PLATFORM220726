# IMP-023 Feature Schema 1.2

Status: Rejected after Train/Validation evaluation; reverted with user approval.

Candidate diagnostics on Feature Schema 1.1.0 showed that the canonical Trend feature had only three distinct values. This is insufficient for an offline classifier to distinguish variations in trend pressure.

Feature Schema 1.2.0 kept the same four canonical feature groups and their fixed CSV order. It changed only their encodings:

- Trend: `CTrendAssembler` now calculates `FeatureStrength` continuously from normalized EMA separation, normalized EMA slope, structure, break of structure, and a CHOCH penalty. The existing `Trend.Strength` is unchanged and remains the value used by the Decision runtime.
- Volatility: ATR ratio is symmetrically encoded around a neutral ratio of 1.0, so below-normal and above-normal volatility occupy distinguishable regions of the 0..100 scale.
- Liquidity: unchanged score.
- Session: unchanged Asia/London/New York encoding of 25/50/75.

The experiment was evaluated on a newly regenerated Schema 1.2.0 dataset using Train and Validation only. Its selected candidate, `random_forest_depth_8_hold_4`, obtained Validation macro F1 `0.3889`, accuracy `0.4420`, and BUY precision `0.4597`. It failed the evaluation gate and was worse than the Schema 1.1.0 candidate's macro F1 `0.4076`.

The Test partition was not read. Schema 1.2.0 code, CSV partitions, diagnostic reports, and preliminary artifacts are deprecated. The active contract is restored to Feature Schema 1.1.0 and Label Schema 1.1.0.
