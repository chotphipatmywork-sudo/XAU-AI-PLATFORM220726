# IMP-017 Model Training Contract

Status: Feature Contract 4.0.0 implemented; MetaEditor and runtime validation passed.

`CModelTrainingContract` is the Phase 7 baseline for framework-independent model training. It establishes the exact twelve-dimension Feature Contract 4.0 order, the SELL/HOLD/BUY label mapping, and the required probability-vector contract. The dimensions remain inside the approved Trend, Volatility, Liquidity, and Session groups. The twelfth field is `session_progress`. The class contains no model weights, no framework dependency, and no order or risk logic.

The focused EA `tests/TestModelTrainingContract.mq5` validates the feature order, label mapping, and a sample valid probability vector.

The contract is documented in `docs/contracts/AI_MODEL_TRAINING_CONTRACT.md`. A future ONNX, TensorFlow, PyTorch, DLL, or REST adapter must conform to this contract instead of changing the Runtime feature definition.

Runtime validation on 2026-07-15 reported Model/Feature/Label contracts `4.0.0/4.0.0/1.1.0`, all twelve ordered input names, the canonical SELL/HOLD/BUY mapping, and a valid probability vector. Deployment remains separately controlled by the Model Evaluation Contract.
