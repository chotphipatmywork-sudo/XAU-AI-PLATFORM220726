# IMP-037 Derived Trend Interaction Diagnostic

Status: Controlled Train-only experiment evaluated; Trend agreement merits bounded nested validation.

## Purpose

IMP-036 found that Trend Regime had a consistent inverse association with the 16-bar label while Trend Momentum and Trend Slope changed directional association across time. `training/trend_interaction_diagnostic.py` tests deterministic interaction candidates derived only from the existing replayed Brain Trend values before proposing any Feature Contract or MQL5 change.

## Candidate interactions

All derived values remain within 0..100:

- Trend extension: absolute Trend Regime distance from neutral 50.
- Regime/Momentum agreement: signed product of centered Regime and Momentum.
- Regime/Slope agreement: signed product of centered Regime and Slope.
- Momentum/Slope agreement: signed product of centered Momentum and Slope.
- Momentum lead over Regime: centered difference between Momentum and Regime.
- Slope lead over Regime: centered difference between Slope and Regime.

The controlled comparison locks expanding history, a raw depth-5 balanced forest, argmax, four Outer periods, and a 16-record purge. Only appended diagnostic interaction columns change. These columns are not active Feature Schema 3.0 inputs.

## Focused validation

`training/test_trend_interaction_diagnostic.py` verifies neutral values, bullish agreement, directional disagreement, bounded feature appending, and the fixed six-set comparison grid. It passed with the feature-label and history-strategy focused tests.

## Result

| Feature set | Macro F1 | BUY precision | BUY recall | Passed folds |
| --- | ---: | ---: | ---: | ---: |
| Trend agreements | 0.3992 | 0.4267 | 0.3899 | 1 |
| All interactions | 0.3950 | 0.4231 | 0.4179 | 0 |
| Extension + agreements | 0.4042 | 0.4205 | 0.3899 | 0 |
| Trend leads | 0.3884 | 0.4192 | 0.4201 | 0 |
| Baseline | 0.3939 | 0.4066 | 0.3721 | 0 |
| Trend extension | 0.3906 | 0.4037 | 0.3866 | 0 |

Trend agreements improved aggregate BUY precision by `0.0201`, BUY recall by `0.0179`, SELL precision by `0.0224`, and produced the first complete passing Fold in the controlled experiments. Fold 2 passed with Accuracy `0.4708`, Macro F1 `0.4445`, BUY precision `0.5153`, and BUY recall `0.4836`.

The improvement was not universal. Agreements slightly degraded Fold 1 and reduced Fold 3 Macro F1, while Fold 4 improved but remained below the gate. All interactions added recall but did not pass a fold, and extension alone ranked below Baseline.

## Decision

Do not change Feature Schema 3.0 or MQL5 yet. Retain only the three agreement candidates for a bounded nested Train-only comparison against Baseline, with the model and argmax policy fixed. Inner folds must choose Baseline or Agreements before each unseen Outer evaluation. Only consistent nested improvement would justify a formal Feature Contract proposal.

IMP-038 completed that nested comparison. All four Outer histories selected Baseline, so the agreement proposal was rejected and Feature Schema 3.0 remains active.
