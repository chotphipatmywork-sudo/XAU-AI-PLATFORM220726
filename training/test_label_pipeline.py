import csv
import json
import tempfile
import unittest
from pathlib import Path

from .label_pipeline import generate_labels, register_label_schema, sha256, validate_labels

class LabelPipelineTests(unittest.TestCase):
    def setup_case(self, root):
        source = Path(root) / "source.csv"
        source.write_text("record_id,symbol,timestamp,approved_label\n2,XAUUSD,2024-01-02,BUY\n1,XAUUSD,2024-01-01,SELL\n", encoding="utf-8")
        schema = register_label_schema("1.0.0", "LABEL-TEST", ["BUY", "SELL"])
        output, manifest = Path(root) / "labels.csv", Path(root) / "manifest.json"
        generate_labels(source, output, manifest, schema, "approved_label", "SRC-TEST", sha256(source))
        return output, manifest, schema

    def test_schema_and_identity(self):
        with tempfile.TemporaryDirectory() as root:
            output, manifest, schema = self.setup_case(root)
            self.assertEqual(validate_labels(output, manifest, schema), [])
            with output.open(newline="", encoding="utf-8") as handle:
                self.assertEqual(next(csv.DictReader(handle))["record_id"], "1")

    def test_deterministic_hash(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            oa, _, _ = self.setup_case(a); ob, _, _ = self.setup_case(b)
            self.assertEqual(sha256(oa), sha256(ob))

    def test_manifest_provenance_linkage(self):
        with tempfile.TemporaryDirectory() as root:
            _, manifest, schema = self.setup_case(root)
            data = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual(data["research_track_id"], "CONTROLLED_RESEARCH_REGENERATION")
            self.assertEqual(data["label_set_id"], schema["label_set_id"])

    def test_reject_record_accounting(self):
        with tempfile.TemporaryDirectory() as root:
            output, manifest, schema = self.setup_case(root); data=json.loads(manifest.read_text()); data["record_count"]=99; manifest.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("record accounting mismatch", validate_labels(output, manifest, schema))

    def test_reject_duplicate(self):
        with tempfile.TemporaryDirectory() as root:
            output, manifest, schema = self.setup_case(root); text = output.read_text(); output.write_text(text + text.splitlines()[1] + "\n", encoding="utf-8")
            self.assertIn("duplicate record_id", validate_labels(output, manifest, schema))

    def test_reject_missing_label(self):
        with tempfile.TemporaryDirectory() as root:
            output, manifest, schema = self.setup_case(root); output.write_text(output.read_text().replace(",BUY,\n", ",,\n"), encoding="utf-8")
            self.assertIn("missing label reason", validate_labels(output, manifest, schema))

    def test_reject_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            output, manifest, schema = self.setup_case(root); data = json.loads(manifest.read_text()); data["label_dataset_sha256"] = "BAD"; manifest.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("manifest/hash mismatch", validate_labels(output, manifest, schema))

if __name__ == "__main__": unittest.main()
