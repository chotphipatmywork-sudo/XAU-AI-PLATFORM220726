# IMP-019 External Training Pipeline

Status: Implemented; baseline Python execution completed for deprecated schema 1.0.0.

The offline `training/train_classifier.py` pipeline consumes the immutable Train, Validation, and Test CSV partitions. It trains a class-balanced logistic-regression baseline using Train only, selects hyperparameters by Validation macro F1, then evaluates the selected model once on Test.

It writes a Python `joblib` artifact and a JSON metadata report containing the exact training-contract schema versions and metrics required by the evaluation contract. The trainer refuses malformed schema, feature values outside 0..100, and labels outside SELL/HOLD/BUY.

The pipeline is intentionally external to MQL5. User-environment execution completed with scikit-learn 1.9.0, and the earlier baseline experiments failed the evaluation gate. Feature Schema 3.0.0 CSV partitions must be regenerated before a new training run; the reader rejects older headers, invalid Liquidity sweep values, and invalid one-hot Session fields. The joblib artifact is not a Runtime deployment artifact; ONNX export and an MQL5 model adapter remain separate tasks.
