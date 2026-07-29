import csv, tempfile, unittest
from pathlib import Path
from .decision_pipeline import FIELDS, generate_manifest, validate_manifest, validate_records

class DecisionPipelineTests(unittest.TestCase):
    def records(self, root, confidence="0.8", decision="BUY"):
        p=Path(root)/"decisions.csv"; rows=[["1","XAUUSD","2024-01-01","AI-1","D-1",decision,confidence,"1.0.0","VALID"]]
        with p.open("w",newline="",encoding="utf-8") as f: w=csv.writer(f,lineterminator="\n"); w.writerow(FIELDS); w.writerows(rows)
        return p
    def test_valid_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.records(root); m=Path(root)/"m.json"; parents={"model_id":"M-1"}; generate_manifest(p,m,parents); self.assertEqual(validate_records(p),[]); self.assertEqual(validate_manifest(p,m,parents),[])
    def test_confidence_rejected(self):
        with tempfile.TemporaryDirectory() as root: self.assertIn("confidence out of range",validate_records(self.records(root,"1.5")))
    def test_prohibited_decision_rejected(self):
        with tempfile.TemporaryDirectory() as root: self.assertIn("prohibited decision status",validate_records(self.records(root,decision="EXECUTE")))
    def test_parent_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.records(root); m=Path(root)/"m.json"; generate_manifest(p,m,{"model_id":"M"}); self.assertIn("parent identity mismatch",validate_manifest(p,m,{"model_id":"OTHER"}))

if __name__ == "__main__": unittest.main()
