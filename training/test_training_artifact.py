import tempfile
import unittest
from pathlib import Path
from .training_artifact import register_artifact, request_promotion, validate_artifact, validate_manifest, write_manifest

class TrainingArtifactTests(unittest.TestCase):
    def record(self): return {"artifact_id":"ART-1","artifact_version":"1.0.0","training_session_id":"S-1","execution_id":"E-1","evaluation_id":"EV-1","model_registry_id":"M-1","status":"DRAFT"}
    def test_register_and_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"artifacts.jsonl"; m=Path(root)/"manifest.json"; register_artifact(h,self.record()); write_manifest(h,m); self.assertEqual(validate_manifest(h,m),[])
    def test_required_linkages(self): self.assertIn("missing evaluation_id",validate_artifact({"artifact_id":"A","status":"DRAFT"}))
    def test_artifact_file_rejected(self):
        with self.assertRaises(ValueError): register_artifact(Path(tempfile.gettempdir())/"x.jsonl",{**self.record(),"artifact_path":"model.bin"})
    def test_promotion_request_is_append_only(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"a.jsonl"; register_artifact(h,self.record()); request_promotion(h,"ART-1","1.0.0","Project Owner"); self.assertEqual(len(h.read_text().splitlines()),2)
    def test_manifest_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"a.jsonl"; m=Path(root)/"m.json"; register_artifact(h,self.record()); write_manifest(h,m); h.write_text(h.read_text()+"\n"); self.assertIn("manifest/hash mismatch",validate_manifest(h,m))

if __name__ == "__main__": unittest.main()
