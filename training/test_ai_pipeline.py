import csv
import tempfile
import unittest
from pathlib import Path
from .ai_pipeline import generate_manifest, validate_manifest, validate_records, sha256

class AIPipelineTests(unittest.TestCase):
    def make_records(self, root):
        p=Path(root)/"ai.csv"; fields=["record_id","symbol","timestamp","research_track_id","dataset_identity","feature_set_version","label_set_version","training_session_id","execution_id","evaluation_id","model_id","ai_configuration_version","output_status"]
        rows=[["1","XAUUSD","2024-01-01","TRACK","DATA","1.0.0","1.0.0","S","E","EV","M","1.0.0","VALID"]]
        with p.open("w",newline="",encoding="utf-8") as f: w=csv.writer(f,lineterminator="\n"); w.writerow(fields); w.writerows(rows)
        return p
    def test_manifest_and_validation(self):
        with tempfile.TemporaryDirectory() as root:
            records=self.make_records(root); manifest=Path(root)/"m.json"; parents={"dataset_identity":"DATA","model_id":"M"}; generate_manifest(records,manifest,parents,"1.0.0"); self.assertEqual(validate_records(records),[]); self.assertEqual(validate_manifest(records,manifest,parents),[])
    def test_deterministic_hash(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b: self.assertEqual(sha256(self.make_records(a)),sha256(self.make_records(b)))
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.make_records(root); p.write_text(p.read_text()+p.read_text().splitlines()[1]+"\n",encoding="utf-8"); self.assertIn("duplicate record_id",validate_records(p))
    def test_parent_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.make_records(root); m=Path(root)/"m.json"; generate_manifest(p,m,{"dataset_identity":"DATA"},"1.0.0"); self.assertIn("parent identity mismatch",validate_manifest(p,m,{"dataset_identity":"OTHER"}))

if __name__ == "__main__": unittest.main()
