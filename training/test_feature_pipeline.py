import csv
import json
import tempfile
import unittest
from pathlib import Path

from .feature_pipeline import FEATURE_NAMES, generate_features, sha256, validate_features


class FeaturePipelineTests(unittest.TestCase):
    def source(self, root):
        path = Path(root) / "source.csv"
        path.write_text("record_id,symbol,timestamp,open,high,low,close\n1,XAUUSD,2024-01-01T00:00:00Z,10,12,9,11\n2,XAUUSD,2024-01-01T00:05:00Z,11,13,10,12\n3,XAUUSD,2024-01-01T00:10:00Z,12,14,11,13\n4,XAUUSD,2024-01-01T00:15:00Z,13,15,12,14\n", encoding="utf-8")
        return path

    def generate_case(self, root, name="out"):
        source = self.source(root); output = Path(root) / (name + ".csv"); manifest = Path(root) / (name + ".json")
        generate_features(source, output, manifest, "SRC-DATA-1", sha256(source))
        return source, output, manifest

    def test_deterministic_and_identity(self):
        with tempfile.TemporaryDirectory() as root:
            _, output, manifest = self.generate_case(root)
            self.assertEqual(validate_features(output, manifest), [])
            with output.open(newline="", encoding="utf-8") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(list(row)[:3], ["record_id", "symbol", "timestamp"])

    def test_no_lookahead(self):
        with tempfile.TemporaryDirectory() as root:
            source, output, _ = self.generate_case(root)
            before = output.read_text()
            source.write_text(source.read_text().replace(",14\n", ",140\n"), encoding="utf-8")
            generate_features(source, output, Path(root) / "changed.json", "SRC-DATA-1", sha256(source))
            self.assertNotEqual(before, output.read_text())
            with output.open(newline="", encoding="utf-8") as handle:
                self.assertEqual(next(csv.DictReader(handle))["return_1"], "")

    def test_manifest_schema(self):
        with tempfile.TemporaryDirectory() as root:
            _, _, manifest = self.generate_case(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["feature_names"], list(FEATURE_NAMES))
            self.assertFalse(data["labels_generated"])

    def test_reject_duplicate(self):
        with tempfile.TemporaryDirectory() as root:
            _, output, manifest = self.generate_case(root)
            text = output.read_text(); output.write_text(text + text.splitlines()[1] + "\n", encoding="utf-8")
            self.assertIn("duplicate record_id", validate_features(output, manifest))

    def test_reject_missing_column(self):
        with tempfile.TemporaryDirectory() as root:
            _, output, manifest = self.generate_case(root)
            output.write_text(output.read_text().replace(",return_3", ",missing"), encoding="utf-8")
            self.assertTrue(validate_features(output, manifest))

    def test_reject_nonfinite(self):
        with tempfile.TemporaryDirectory() as root:
            _, output, manifest = self.generate_case(root)
            output.write_text(output.read_text().replace("1.000000000000", "nan", 1), encoding="utf-8")
            self.assertIn("invalid or non-finite feature value", validate_features(output, manifest))

    def test_warmup_null_and_unexpected_null(self):
        with tempfile.TemporaryDirectory() as root:
            _, output, manifest = self.generate_case(root)
            self.assertEqual(validate_features(output, manifest), [])
            output.write_text(output.read_text().replace("0.090909090909", "", 1), encoding="utf-8")
            self.assertIn("unexpected empty feature value", validate_features(output, manifest))

    def test_reject_manifest_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            _, output, manifest = self.generate_case(root)
            data = json.loads(manifest.read_text()); data["feature_dataset_sha256"] = "BAD"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("manifest/hash mismatch", validate_features(output, manifest))

    def test_reject_column_order(self):
        with tempfile.TemporaryDirectory() as root:
            _, output, manifest = self.generate_case(root)
            lines = output.read_text().splitlines(); columns = lines[0].split(","); columns[3], columns[4] = columns[4], columns[3]
            output.write_text(",".join(columns) + "\n" + "\n".join(lines[1:]) + "\n", encoding="utf-8")
            self.assertIn("non-deterministic feature ordering or columns", validate_features(output, manifest))


if __name__ == "__main__":
    unittest.main()
