# IMP-043 Session Progress Context Diagnostic

Status: Controlled Train-only experiment evaluated; bounded nested confirmation required.

## Purpose

IMP-041 found that the Session group produced the largest local true-label support gain, while the existing three one-hot fields could not express where a bar occurs inside its eight-hour session. `training/session_context_diagnostic.py` tests one future-safe scalar derived from the timestamp already stored in every dataset row.

## Candidate

`session_progress` maps elapsed minutes inside the active eight-hour session to `0..100`:

```text
100 * elapsed session minutes / 480
```

Examples are `00:00 = 0`, `04:00 = 50`, `08:00 = 0`, `12:00 = 50`, and `23:45 = 96.875`. The existing Asia/London/New York one-hot fields remain unchanged. The candidate belongs to the canonical Session group and uses no future price, label, risk, confidence, or execution result.

## Fixed comparison

- Candidate sets: Schema 3.0 Baseline or Baseline plus Session Progress.
- Model: raw depth-5 balanced random forest.
- Policy: argmax.
- History: expanding.
- Evaluation: four chronological Train-only periods with a 16-record purge.
- Validation and Test are never read.

## Focused validation

`training/test_session_context_diagnostic.py` verifies all three session boundaries, mid-session values, the final M15 slot, deterministic feature appending, and source immutability. It passed.

## Result

| Feature set | Accuracy | Macro F1 | SELL precision | BUY precision | BUY recall | Gate floor | Passed folds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 0.4107 | 0.3939 | 0.5425 | 0.4066 | 0.3721 | 0.8132 | 0 |
| Session Progress | 0.4167 | 0.4005 | 0.5363 | 0.4221 | 0.3721 | 0.8441 | 0 |

Session Progress improved Macro F1 in folds 1, 3, and 4, while fold 2 declined slightly. It improved aggregate BUY precision by `0.0155` and the weakest gate ratio by `0.0309`, but no complete fold passed.

## Decision

Do not change MQL5 or Feature Schema 3.0 from the controlled result alone. Advance only Session Progress to a bounded nested Baseline comparison with the model and policy fixed. IMP-044 records that confirmation.

