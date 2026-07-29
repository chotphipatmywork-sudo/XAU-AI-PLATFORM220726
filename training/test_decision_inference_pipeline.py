import csv
import tempfile
import unittest
from pathlib import Path

from training.decision_inference_pipeline import FIELDS, generate_manifest, integrate, validate_manifest, validate_records


def write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


class DecisionInferenceTests(unittest.TestCase):
    def test_join_and_manifest_are_deterministic(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            d = base / "d.csv"
            i = base / "i.csv"
            out = base / "out.csv"
            manifest = base / "manifest.json"
            write_csv(d, ["record_id", "symbol", "timestamp", "decision_id", "decision", "status"], [{"record_id":"r1","symbol":"XAUUSD","timestamp":"2026-01-01T00:00:00Z","decision_id":"d1","decision":"BUY","status":"OBSERVE"}])
            write_csv(i, ["record_id", "symbol", "timestamp", "inference_id", "model_id", "model_version", "feature_set_version", "configuration_version", "output", "confidence", "status"], [{"record_id":"r1","symbol":"XAUUSD","timestamp":"2026-01-01T00:00:00Z","inference_id":"i1","model_id":"m1","model_version":"1.0.0","feature_set_version":"1.0.0","configuration_version":"1.0.0","output":"BUY","confidence":"0.8","status":"OBSERVE"}])
            integrate(d, i, out)
            self.assertEqual(validate_records(out), [])
            generate_manifest(out, manifest, {"decision": "dhash", "inference": "ihash"})
            self.assertEqual(validate_manifest(out, manifest, {"decision": "dhash", "inference": "ihash"}), [])

    def test_rejects_join_mismatch_and_duplicate(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            d, i = base / "d.csv", base / "i.csv"
            write_csv(d, ["record_id"], [{"record_id":"r1"}, {"record_id":"r1"}])
            write_csv(i, ["record_id"], [{"record_id":"r1"}])
            with self.assertRaises(ValueError):
                integrate(d, i, base / "out.csv")

    def test_manifest_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "out.csv"
            row = {field: "x" for field in FIELDS}
            row.update(record_id="r1", symbol="XAUUSD", timestamp="2026-01-01T00:00:00Z", confidence="0.5")
            write_csv(path, list(FIELDS), [row])
            manifest = Path(root) / "manifest.json"
            generate_manifest(path, manifest, {})
            path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            self.assertIn("manifest/hash mismatch", validate_manifest(path, manifest, {}))


if __name__ == "__main__":
    unittest.main()
