# IMP-020 Candidate Model Diagnostics

Status: Implemented; Train/Validation-only candidate sweep.

`training/select_candidate.py` compares a majority baseline, class-balanced logistic regression, balanced random forests, and fixed HOLD weights of 2 and 4, plus a bounded Extra Trees candidate. The HOLD=2 variants are a limited follow-up sweep after Schema 1.1 validation showed excessive false HOLD predictions. The script selects a candidate that meets the Validation gate first; when none meet it, it selects by Validation macro F1 and then accuracy. Every candidate report includes `validation_gate_met`.

The script deliberately accepts no Test file and records `test_dataset_used: false` in its JSON report. The existing Test partition was already observed during the baseline evaluation, so it must not influence candidate selection. After a candidate is selected, a newly generated later-period Test partition is required for final evaluation.

The report also records class distributions and Train feature means by SELL/HOLD/BUY. This is diagnostic evidence only; it does not add or alter the canonical four-feature model input.

The schema 1.0.0 diagnostic exposed constant Trend and Session values. Candidate results from that schema are deprecated by the schema 1.1.0 feature projection correction. Schema 1.2 was evaluated and rejected without reading its Test partition.
