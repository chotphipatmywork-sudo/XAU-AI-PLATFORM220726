"""Focused tests for the future-safe Session context diagnostic."""

from datetime import datetime

from session_context_diagnostic import append_session_progress, parse_timestamp, session_progress


def main() -> None:
    cases = {
        "2026.07.15 00:00:00": 0.0,
        "2026.07.15 04:00:00": 50.0,
        "2026.07.15 08:00:00": 0.0,
        "2026.07.15 12:00:00": 50.0,
        "2026.07.15 16:00:00": 0.0,
        "2026.07.15 20:00:00": 50.0,
        "2026.07.15 23:45:00": 96.875,
    }
    for text, expected in cases.items():
        actual = session_progress(parse_timestamp(text))
        if abs(actual - expected) > 1e-12:
            raise AssertionError(f"Unexpected Session progress for {text}: {actual}")

    source = [[10.0], [20.0]]
    timestamps = [datetime(2026, 7, 15, 1, 0), datetime(2026, 7, 15, 10, 0)]
    transformed = append_session_progress(source, timestamps)
    if transformed != [[10.0, 12.5], [20.0, 25.0]]:
        raise AssertionError("Session progress was not appended deterministically")
    if source != [[10.0], [20.0]]:
        raise AssertionError("Source features must not be mutated")

    print("Session context diagnostic test passed")


if __name__ == "__main__":
    main()
