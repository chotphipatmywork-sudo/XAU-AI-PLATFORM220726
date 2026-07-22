# IMP-018 Model Evaluation Contract

Status: Implemented; pending MetaEditor compilation validation.

`CModelEvaluationContract` validates framework-reported Validation and Test metrics and checks them against baseline thresholds. `CModelEvaluationMetrics` holds raw metrics; `CModelEvaluationReport` states whether the model is eligible for shadow deployment.

The contract requires macro F1 and directional precision/recall in addition to accuracy, because the current historical labels contain relatively few HOLD samples. Both evaluation partitions must pass all thresholds.

`tests/TestModelEvaluationContract.mq5` supplies valid sample metrics for the existing 486/487 Validation/Test partition sizes. It validates the contract only; it does not train, load, or trade a model.
