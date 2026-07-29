import csv, tempfile, unittest
from pathlib import Path
from .inference_pipeline import FIELDS, generate_manifest, validate_manifest, validate_records

class InferencePipelineTests(unittest.TestCase):
    def records(self, root, confidence="0.7"):
        p=Path(root)/"inference.csv"; row=["1","XAUUSD","2024-01-01","I-1","M-1","1.0.0","1.0.0","1.0.0","BUY",confidence,"VALID"]
        with p.open("w",newline="",encoding="utf-8") as f: w=csv.writer(f,lineterminator="\n"); w.writerow(FIELDS); w.writerow(row)
        return p
    def test_valid_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.records(root); m=Path(root)/"m.json"; parents={"model_id":"M-1"}; generate_manifest(p,m,parents); self.assertEqual(validate_records(p),[]); self.assertEqual(validate_manifest(p,m,parents),[])
    def test_confidence_rejected(self):
        with tempfile.TemporaryDirectory() as root: self.assertIn("confidence out of range",validate_records(self.records(root,"1.2")))
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.records(root); p.write_text(p.read_text()+p.read_text().splitlines()[1]+"\n",encoding="utf-8"); self.assertIn("duplicate record_id",validate_records(p))
    def test_manifest_parent_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            p=self.records(root); m=Path(root)/"m.json"; generate_manifest(p,m,{"model_id":"M"}); self.assertIn("parent identity mismatch",validate_manifest(p,m,{"model_id":"OTHER"}))

if __name__ == "__main__": unittest.main()
