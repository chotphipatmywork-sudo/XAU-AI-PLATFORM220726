"""Focused checks for the validation-only probability decision policy."""

from select_candidate import predict_with_policy


def main() -> None:
    policy = {"type": "confidence", "sell_minimum": 0.50, "buy_minimum": 0.50, "margin": 0.05}
    probabilities = [
        [0.70, 0.20, 0.10],
        [0.20, 0.20, 0.60],
        [0.42, 0.32, 0.26],
        [0.48, 0.05, 0.47],
    ]
    predicted = predict_with_policy(probabilities, [-1, 0, 1], policy)
    if predicted != [-1, 1, 0, 0]:
        raise AssertionError(f"Unexpected confidence policy predictions: {predicted}")

    argmax = predict_with_policy(probabilities, [-1, 0, 1], {"type": "argmax"})
    if argmax != [-1, 1, -1, -1]:
        raise AssertionError(f"Unexpected argmax policy predictions: {argmax}")

    margin_only = {"type": "confidence", "sell_minimum": 0.00, "buy_minimum": 0.00, "margin": 0.05}
    margin_prediction = predict_with_policy(probabilities, [-1, 0, 1], margin_only)
    if margin_prediction != [-1, 1, -1, 0]:
        raise AssertionError(f"Unexpected margin policy predictions: {margin_prediction}")

    print("Probability decision policy test passed")


if __name__ == "__main__":
    main()
