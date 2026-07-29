import csv
import tempfile
import unittest
from pathlib import Path

from training.backtest_pipeline import generate_manifest, run_backtest, validate_events, validate_manifest


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


class BacktestTests(unittest.TestCase):
    def test_causal_entry_and_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root); decisions = base / "d.csv"; bars = base / "b.csv"; events = base / "e.csv"; manifest = base / "m.json"
            write(decisions, ["record_id", "symbol", "timestamp", "decision_id", "side", "quantity"], [{"record_id":"r1","symbol":"XAUUSD","timestamp":"2026-01-01T00:00:00Z","decision_id":"d1","side":"BUY","quantity":"1"}])
            write(bars, ["symbol", "timestamp", "bid", "ask"], [{"symbol":"XAUUSD","timestamp":"2026-01-01T00:00:00Z","bid":"2000","ask":"2001"}])
            run_backtest(decisions, bars, events)
            self.assertEqual(validate_events(events), [])
            generate_manifest(events, manifest, {"decisions":"d1", "bars":"b1"})
            self.assertEqual(validate_manifest(events, manifest, {"decisions":"d1", "bars":"b1"}), [])

    def test_missing_bar_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root); d = base / "d.csv"; b = base / "b.csv"
            write(d, ["record_id", "symbol", "timestamp", "decision_id", "side", "quantity"], [{"record_id":"r1","symbol":"XAUUSD","timestamp":"t1","decision_id":"d1","side":"BUY","quantity":"1"}])
            write(b, ["symbol", "timestamp", "bid", "ask"], [])
            with self.assertRaises(ValueError): run_backtest(d, b, base / "e.csv")

    def test_manifest_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root); e = base / "e.csv"
            write(e, ["record_id", "symbol", "timestamp", "decision_id", "event_id", "event_type", "side", "price", "quantity", "status"], [{"record_id":"r1","symbol":"XAUUSD","timestamp":"2026-01-01T00:00:00Z","decision_id":"d1","event_id":"e1","event_type":"ENTRY","side":"BUY","price":"1","quantity":"1","status":"RESEARCH_ONLY"}])
            m = base / "m.json"; generate_manifest(e, m, {})
            e.write_text(e.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.assertIn("manifest/hash mismatch", validate_manifest(e, m, {}))

    def test_rejects_nonfinite_and_non_utc_events(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "events.csv"
            write(path, ["record_id", "symbol", "timestamp", "decision_id", "event_id", "event_type", "side", "price", "quantity", "status"], [{"record_id":"r1","symbol":"XAUUSD","timestamp":"2026-01-01T00:00:00","decision_id":"d1","event_id":"e1","event_type":"ENTRY","side":"BUY","price":"NaN","quantity":"1","status":"RESEARCH_ONLY"}])
            errors = validate_events(path)
            self.assertIn("invalid price or quantity", errors)
            self.assertIn("timestamp is not UTC", errors)

    def test_rejects_duplicate_decisions(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root); d = base / "d.csv"; b = base / "b.csv"
            row = {"record_id":"r1","symbol":"XAUUSD","timestamp":"2026-01-01T00:00:00Z","decision_id":"d1","side":"BUY","quantity":"1"}
            write(d, list(row), [row, row])
            write(b, ["symbol", "timestamp", "bid", "ask"], [{"symbol":"XAUUSD","timestamp":"2026-01-01T00:00:00Z","bid":"2000","ask":"2001"}])
            with self.assertRaises(ValueError): run_backtest(d, b, base / "e.csv")


if __name__ == "__main__": unittest.main()
