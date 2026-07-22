# IMP-041 Train-only Feature Sufficiency Diagnostic

Status: Evaluated; Feature Schema 3.0 has measurable but weak local label separation.

## Purpose

IMP-040 found that adding past-only Trend changes did not generalize through nested Outer periods. `training/feature_sufficiency_diagnostic.py` tests a more fundamental question: when Schema 3.0 feature rows are similar, are their approved 16-bar labels also consistent?

This distinguishes a model-search problem from a representation/target-overlap problem before more model complexity is introduced.

## Method

- Source: purged Train partition only (`4,659` records).
- Evaluation: four expanding chronological periods with a 16-record purge.
- Reference rows: past training history only.
- Distance: standardized Euclidean distance.
- Default neighbourhood: 25 nearest past rows.
- Views: full Schema 3.0, non-Session, and each canonical Trend, Volatility, Liquidity, and Session group.
- Validation and Test are never read.

The primary measurement is true-label support: the fraction of neighbouring past rows that share the evaluation row's actual label. This is compared with the same label's unconditional frequency in the available training history. Normalized entropy measures local label mixing, where `0` is pure and `1` is maximally mixed.

## Focused validation

`training/test_feature_sufficiency_diagnostic.py` verifies active contract-version metadata, entropy boundaries, deterministic label ties, the Schema 4.0 group map, and a separable synthetic neighbourhood with exact label recovery.

## Result

For the complete Schema 3.0 view with 25 neighbours:

- Mean true-label support: `0.4256`.
- Historical-frequency support: `0.4128`.
- Local support gain: `0.0128` (1.28 percentage points).
- Mean neighbourhood purity: `0.5576`.
- Mean normalized label entropy: `0.7596`.
- Nearest-row label match: `0.4266`.
- Rows with true-label support below one third: `0.2794`.
- Local-majority Accuracy/Macro F1: `0.4558 / 0.3788`.

The full-view support gain remained small under neighbourhood sensitivity checks:

| Neighbours | True-label support | Gain over history | Entropy | Macro F1 |
| ---: | ---: | ---: | ---: | ---: |
| 15 | 0.4259 | 0.0131 | 0.7162 | 0.3760 |
| 25 | 0.4256 | 0.0128 | 0.7596 | 0.3788 |
| 50 | 0.4228 | 0.0100 | 0.7987 | 0.3727 |

The HOLD class was especially ambiguous. Its mean true-label support across the four full-schema periods ranged from `0.1668` to `0.2429`, materially below directional-class support.

Session alone showed the largest support gain, but its local-majority prediction emitted no BUY labels and had Macro F1 `0.2918`. This reflects session-conditioned class frequency rather than sufficient directional information. Liquidity alone added only `0.0014` support over history.

## Interpretation

Schema 3.0 contains real association: nearby rows are slightly more label-consistent than unconditional history. However, high local entropy and the small, sensitivity-stable support gain show substantial overlap between SELL/HOLD/BUY under the fixed 16-bar triple-barrier target. A more complex classifier can partition the same overlap differently, but the current evidence does not support expecting model complexity alone to reach a stable deployment gate.

This is a diagnostic association, not an estimate of causal value or a mathematical upper bound on achievable accuracy.

## Decision

Keep Feature Schema 3.0 and Label Schema 1.1 unchanged. Do not deploy, regenerate datasets, or add new MQL5 fields from this result.

The next bounded step is a Train-only confidence-versus-coverage diagnostic using the already fixed model family. It should determine whether a small subset of highly confident directional predictions is stable enough to justify a separately nested abstention-policy experiment. If no stable high-precision region exists, further threshold search should stop and the project should prepare a separately approved Brain-context proposal instead.

## Expanded Schema 4.0 result

The final phase diagnostic used the 18,788-record expanded Train partition and 25 nearest past neighbours. Validation and Test were not read.

For the complete twelve-field Schema 4.0 view:

- mean true-label support: `0.4278`
- support gain over historical class frequency: `0.0207`
- normalized label entropy: `0.7437`
- nearest-row label match: `0.4314`
- local-majority Accuracy/Macro F1: `0.4517 / 0.3990`
- local-majority BUY precision/recall: `0.4718 / 0.4985`

The Session group produced the strongest view with Macro F1 `0.4240`, but BUY precision was `0.4853` and SELL precision was `0.4691`. Schema 4.0 therefore contains measurable local information, especially in Session context, while still exhibiting substantial three-class overlap and insufficient directional precision.

This confirms that additional classifier complexity alone is not a credible path to the deployment gate under the inspected Feature/Label Contract.
