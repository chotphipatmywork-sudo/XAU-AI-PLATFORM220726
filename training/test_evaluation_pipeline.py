import json
import tempfile
import unittest
from pathlib import Path

from .evaluation_pipeline import evaluate, sha256, validate_input, validate_manifest

class EvaluationPipelineTests(unittest.TestCase):
    def make_input(self, root):
        path=Path(root)/"predictions.csv"
        path.write_text("record_id,symbol,timestamp,actual,predicted\n1,XAUUSD,2024-01-01,BUY,BUY\n2,XAUUSD,2024-01-02,SELL,BUY\n",encoding="utf-8")
        return path
    def test_input_validation(self):
        with tempfile.TemporaryDirectory() as root: self.assertEqual(validate_input(self.make_input(root))[0],[])
    def test_accuracy(self):
        with tempfile.TemporaryDirectory() as root:
            source=self.make_input(root); manifest=Path(root)/"evaluation.json"; data=evaluate(source,manifest,"DATA-1","MODEL-1"); self.assertEqual(data["metrics"]["accuracy"],0.5)
    def test_manifest_validation(self):
        with tempfile.TemporaryDirectory() as root:
            source=self.make_input(root); manifest=Path(root)/"evaluation.json"; evaluate(source,manifest,"DATA-1","MODEL-1"); self.assertEqual(validate_manifest(source,manifest,"DATA-1","MODEL-1"),[])
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            source=self.make_input(root); source.write_text(source.read_text()+"1,XAUUSD,2024-01-03,BUY,BUY\n",encoding="utf-8"); self.assertIn("duplicate record_id",validate_input(source)[0])
    def test_hash_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            source=self.make_input(root); manifest=Path(root)/"evaluation.json"; evaluate(source,manifest,"DATA-1","MODEL-1"); source.write_text(source.read_text()+"3,XAUUSD,2024-01-03,BUY,BUY\n",encoding="utf-8"); self.assertIn("manifest/hash mismatch",validate_manifest(source,manifest,"DATA-1","MODEL-1"))

if __name__ == "__main__": unittest.main()
