import tempfile
import unittest
from pathlib import Path
from .model_registry import register_model, transition_model, validate_registry, write_manifest

class ModelRegistryTests(unittest.TestCase):
    def record(self):
        return {"model_id":"MODEL-1","model_version":"1.0.0","training_run_id":"RUN-1","evaluation_id":"EVAL-1","dataset_identity":"DATA-1","feature_schema_version":"1.0.0","label_schema_version":"1.0.0","status":"DRAFT"}
    def test_register_and_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            registry=Path(root)/"models.jsonl"; manifest=Path(root)/"manifest.json"; register_model(registry,self.record()); write_manifest(registry,manifest); self.assertEqual(validate_registry(registry,manifest),[])
    def test_semver_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            bad=self.record(); bad["model_version"]="1.0";
            with self.assertRaises(ValueError): register_model(Path(root)/"r.jsonl",bad)
    def test_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            registry=Path(root)/"r.jsonl"; register_model(registry,self.record());
            with self.assertRaises(ValueError): register_model(registry,self.record())
    def test_lifecycle(self):
        with tempfile.TemporaryDirectory() as root:
            r=Path(root)/"r.jsonl"; register_model(r,self.record()); transition_model(r,"MODEL-1","1.0.0","CANDIDATE"); transition_model(r,"MODEL-1","1.0.0","APPROVED"); self.assertEqual(len(r.read_text().splitlines()),3)
    def test_retired_cannot_transition(self):
        with tempfile.TemporaryDirectory() as root:
            r=Path(root)/"r.jsonl"; x=self.record(); x["status"]="RETIRED"; register_model(r,x)
            with self.assertRaises(ValueError): transition_model(r,"MODEL-1","1.0.0","DRAFT")

if __name__ == "__main__": unittest.main()
