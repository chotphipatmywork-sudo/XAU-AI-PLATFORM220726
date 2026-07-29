import tempfile
import unittest
from pathlib import Path
from .training_session import config_hash, create_session, transition_session, validate_configuration, validate_manifest, write_manifest

class TrainingSessionTests(unittest.TestCase):
    def config(self): return {"dataset_identity":"DATA-1","feature_schema_version":"1.0.0","label_schema_version":"1.0.0","configuration_version":"1.0.0","model_training":False}
    def test_create_and_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"history.jsonl"; m=Path(root)/"manifest.json"; create_session(h,"SESSION-1","JOB-1",self.config()); write_manifest(h,m,"SESSION-1"); self.assertEqual(validate_manifest(h,m,"SESSION-1"),[])
    def test_config_hash_deterministic(self): self.assertEqual(config_hash({"b":2,"a":1}),config_hash({"a":1,"b":2}))
    def test_invalid_configuration(self): self.assertIn("model training is prohibited",validate_configuration({**self.config(),"model_training":True}))
    def test_lifecycle_history(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"h.jsonl"; create_session(h,"S","J",self.config()); transition_session(h,"S","READY"); transition_session(h,"S","RUNNING"); transition_session(h,"S","COMPLETED"); self.assertEqual(len(h.read_text().splitlines()),4)
    def test_invalid_transition(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"h.jsonl"; create_session(h,"S","J",self.config());
            with self.assertRaises(ValueError): transition_session(h,"S","COMPLETED")

if __name__ == "__main__": unittest.main()
