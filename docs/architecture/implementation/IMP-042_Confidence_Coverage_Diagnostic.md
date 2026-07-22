# IMP-042 Train-only Confidence-versus-Coverage Diagnostic

Status: Evaluated; further confidence-threshold search stopped.

## Purpose

IMP-041 found substantial local label overlap under Feature Schema 3.0. `training/confidence_coverage_diagnostic.py` tests whether the already fixed model nevertheless contains a smaller, consistently reliable subset of directional predictions that could justify a later nested abstention-policy experiment.

## Fixed method

- Data: purged Train partition only.
- Model: raw depth-5 balanced random forest.
- Evaluation: four expanding chronological folds with a 16-record purge.
- Policy: symmetric SELL/BUY confidence floor; otherwise HOLD.
- Fixed diagnostic thresholds: `0.34, 0.38, 0.42, 0.46, 0.50, 0.55, 0.60, 0.65, 0.70`.
- Minimum support for a per-fold precision conclusion: 25 SELL and 25 BUY predictions.
- Validation and Test are never read.

No threshold is selected or locked by this diagnostic.

## Focused validation

`training/test_confidence_coverage_diagnostic.py` verifies active contract-version metadata, the fixed threshold grid, symmetric policy contract, canonical prediction counts, coverage, support floor, and directional precision gate.

## Result

| Threshold | Directional coverage | SELL precision | BUY precision | SELL recall | BUY recall | Folds passing precision gate |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.34 | 0.7279 | 0.5426 | 0.4074 | 0.4044 | 0.3709 | 0 |
| 0.38 | 0.6352 | 0.5547 | 0.4110 | 0.3519 | 0.3352 | 0 |
| 0.42 | 0.4845 | 0.5556 | 0.4168 | 0.2623 | 0.2659 | 0 |
| 0.46 | 0.2940 | 0.5344 | 0.4411 | 0.1447 | 0.1799 | 1 |
| 0.50 | 0.0820 | 0.5487 | 0.3846 | 0.0525 | 0.0335 | 0 |
| 0.55 | 0.0056 | 1.0000 | 0.2500 | 0.0008 | 0.0034 | 0 |
| 0.60 | 0.0017 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 |
| 0.65 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 |
| 0.70 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0 |

At `0.46`, only one fold met both supported directional precision requirements. At `0.50`, individual folds became directionally asymmetric: some produced almost only SELL, some almost only BUY, and one produced no SELL predictions. Above `0.55`, sample support collapsed and precision values were no longer meaningful.

## Decision

Do not proceed to nested confidence-policy selection and do not tune additional probability thresholds on these inspected Train periods. There is no stable high-confidence directional region under the fixed model and Schema 3.0 representation.

Keep the deployment gate closed. Validation and Test remain untouched, and no MQL5/model artifact is authorized for shadow or live use.

The next material improvement requires new market context from the Brain layer rather than more threshold search or more derivatives of the same Trend snapshot. Because that would change the public Feature Contract and historical dataset schema, it must begin with an explicit proposal and user approval before any MQL5 implementation.

## Expanded Schema 4.0 result

The fixed threshold frontier was repeated on the expanded Train partition. Validation and Test were not read.

- At `0.34`, directional coverage was `73.04%`; SELL/BUY precision was `0.4621 / 0.4934`.
- At `0.46`, directional coverage fell to `22.00%`; SELL/BUY precision was `0.4848 / 0.5005`, with SELL/BUY recall only `0.1322 / 0.1120`.
- At `0.50`, directional coverage collapsed to `3.26%`; BUY precision rose to `0.5844`, but SELL precision fell to `0.4145` and both recalls were near zero.
- No threshold passed the supported directional-precision requirement in every fold.

The larger dataset confirms that there is no stable confidence-only deployment region. Threshold search is closed for this phase.
