import json
import tempfile
import unittest
from pathlib import Path

from .training_pipeline import assemble_dataset, sha256, validate_dataset

class TrainingPipelineTests(unittest.TestCase):
    def make_inputs(self, root):
        root=Path(root); features=root/"features.csv"; labels=root/"labels.csv"
        features.write_text("record_id,symbol,timestamp,return_1\n2,XAUUSD,2024-01-02,0.2\n1,XAUUSD,2024-01-01,0.1\n",encoding="utf-8")
        labels.write_text("record_id,symbol,timestamp,label\n2,XAUUSD,2024-01-02,BUY\n1,XAUUSD,2024-01-01,SELL\n",encoding="utf-8")
        return features,labels
    def test_assembly_split_and_identity(self):
        with tempfile.TemporaryDirectory() as root:
            f,l=self.make_inputs(root); out=Path(root)/"train.csv"; m=Path(root)/"manifest.json"; assemble_dataset(f,l,out,m,"2024-01-02","2024-01-03")
            self.assertEqual(validate_dataset(out,m,"2024-01-02","2024-01-03"),[]); self.assertTrue(out.read_text().splitlines()[1].startswith("1,XAUUSD,2024-01-01"))
    def test_missing_join_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            f,l=self.make_inputs(root); l.write_text(l.read_text().replace("2,XAUUSD,2024-01-02,BUY\n",""),encoding="utf-8")
            with self.assertRaises(ValueError): assemble_dataset(f,l,Path(root)/"o.csv",Path(root)/"m.json","2024-01-02","2024-01-03")
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            f,l=self.make_inputs(root); f.write_text(f.read_text()+"1,XAUUSD,2024-01-01,0.1\n",encoding="utf-8")
            with self.assertRaises(ValueError): assemble_dataset(f,l,Path(root)/"o.csv",Path(root)/"m.json","2024-01-02","2024-01-03")
    def test_manifest_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            f,l=self.make_inputs(root); o=Path(root)/"o.csv"; m=Path(root)/"m.json"; assemble_dataset(f,l,o,m,"2024-01-02","2024-01-03"); d=json.loads(m.read_text()); d["training_dataset_sha256"]="BAD"; m.write_text(json.dumps(d)); self.assertIn("manifest/hash mismatch",validate_dataset(o,m,"2024-01-02","2024-01-03"))
    def test_repeated_hash_is_stable(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            fa,la=self.make_inputs(a); fb,lb=self.make_inputs(b); oa=Path(a)/"o.csv"; ob=Path(b)/"o.csv"; assemble_dataset(fa,la,oa,Path(a)/"m.json","2024-01-02","2024-01-03"); assemble_dataset(fb,lb,ob,Path(b)/"m.json","2024-01-02","2024-01-03"); self.assertEqual(sha256(oa),sha256(ob))

    def test_manifest_identity_linkage(self):
        with tempfile.TemporaryDirectory() as root:
            f,l=self.make_inputs(root); o=Path(root)/"o.csv"; m=Path(root)/"m.json"; assemble_dataset(f,l,o,m,"2024-01-02","2024-01-03")
            data=json.loads(m.read_text(encoding="utf-8"))
            self.assertEqual(data["research_track_id"], "CONTROLLED_RESEARCH_REGENERATION")
            self.assertEqual(data["dataset_identity"], o.stem)

    def test_reject_partition_accounting(self):
        with tempfile.TemporaryDirectory() as root:
            f,l=self.make_inputs(root); o=Path(root)/"o.csv"; m=Path(root)/"m.json"; assemble_dataset(f,l,o,m,"2024-01-02","2024-01-03"); data=json.loads(m.read_text()); data["partition_counts"]["train"]=99; m.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("partition accounting mismatch", validate_dataset(o,m,"2024-01-02","2024-01-03"))

if __name__ == "__main__": unittest.main()
