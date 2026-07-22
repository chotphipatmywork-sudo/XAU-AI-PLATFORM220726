# IMP-027 Probability Decision Policy

Historical status: the recorded experiment used Feature Schema 1.4.0; new experiments must use active Feature Contract 3.0.0 after dataset regeneration.

Status: Evaluated; policy experiment did not pass the Validation gate.

## Purpose

Feature Schema 1.4.0 improved Validation macro F1 but did not meet the directional BUY precision gate. This implementation adds a Training-only decision-policy experiment. It does not change the canonical Brain features, historical labels, AI Runtime, Decision Runtime, Risk, Execution, or Trade Lifecycle.

## Policy

Each candidate model produces the existing three probabilities in the fixed `[SELL, HOLD, BUY]` order. Candidate selection evaluates both ordinary `argmax` and confidence policies. A confidence policy emits a directional label only when:

- its SELL or BUY probability meets its configured minimum; and
- it exceeds the other two probabilities by the configured margin.

Otherwise it emits HOLD. The policy grid includes low confidence floors and margin-only variants because class-balanced models can produce useful relative rankings without probabilities above 0.45. Selection uses Train and Validation only. The Validation gate, feature schema 1.4.0, label schema 1.1.0, and untouched-Test rule remain unchanged.

## Artifact boundary

The selected preliminary joblib is paired with `xau_ai_candidate_preliminary_policy.json`. The policy is metadata for offline evaluation only. A future inference adapter must validate and load both artifacts before any shadow deployment. This implementation does not authorize live trading or alter Risk's final gate.

## Focused validation

Run `training/test_probability_decision_policy.py` with the project virtual environment. It checks deterministic SELL, HOLD, and BUY outcomes for the argmax and confidence paths without reading a dataset.

## Validation result

The focused policy test passed. Candidate selection then evaluated argmax, confidence-floor, margin-only, and combined policies on the 1,001-record Validation partition. No candidate-policy pair passed the evaluation gate, and the selection rule retained `random_forest_depth_10_balanced` with ordinary argmax.

| Metric | Result | Required |
| --- | ---: | ---: |
| Accuracy | 0.4366 | 0.45 |
| Macro F1 | 0.4148 | 0.40 |
| SELL precision | 0.5021 | 0.50 |
| SELL recall | 0.4794 | 0.30 |
| BUY precision | 0.4111 | 0.50 |
| BUY recall | 0.3700 | 0.30 |

Confidence filtering reduced directional recall faster than it improved precision. Therefore the probability policy is retained as an offline experiment but is rejected as the solution for the current candidate. The Test partition remains unread, and the preliminary model is not eligible for MQL5 or trading deployment.
