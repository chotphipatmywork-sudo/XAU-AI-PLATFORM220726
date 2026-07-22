# IMP-024 Feature Diagnostic

Status: Implemented; user-environment Python validation completed without Test access.

`training/diagnose_features.py` is an offline, read-only diagnostic for the preliminary candidate selected by `select_candidate.py`. It reads the existing Train and Validation CSV files, then reports feature ranges, distinct counts, per-class means and standard deviations, the selected tree model's impurity importance, and Validation permutation importance measured as macro-F1 drop.

The diagnostic never accepts a Test path, never trains or changes a model, and never modifies CSV data. Its JSON output is evidence for a later Brain or feature-contract decision only. It does not add a fifth feature, alter the canonical four-feature order, or authorize deployment.

On the 6,679-record Schema 1.1.0 dataset, Trend had only three distinct values and its Validation permutation macro-F1 drop was `0.0025`, making it effectively non-informative for the selected candidate. The corresponding drops were Volatility `0.0300`, Liquidity `0.0499`, and Session `0.0682`. The Test partition was not read. These results justify investigating the underlying Brain Trend signal rather than further classifier-weight tuning.
