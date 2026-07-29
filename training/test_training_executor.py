import tempfile
import unittest
from pathlib import Path
from .training_executor import create_execution, transition_execution, validate_manifest, write_manifest

class TrainingExecutorTests(unittest.TestCase):
    def test_lifecycle_and_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"history.jsonl"; m=Path(root)/"manifest.json"; create_execution(h,"E-1","S-1","HASH"); transition_execution(h,"E-1","RUNNING"); transition_execution(h,"E-1","COMPLETED",{"accuracy":0.5},{"step":1}); write_manifest(h,m,"E-1"); self.assertEqual(validate_manifest(h,m,"E-1"),[])
    def test_invalid_transition(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"h.jsonl"; create_execution(h,"E","S","H")
            with self.assertRaises(ValueError): transition_execution(h,"E","COMPLETED")
    def test_terminal_state(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"h.jsonl"; create_execution(h,"E","S","H"); transition_execution(h,"E","CANCELLED")
            with self.assertRaises(ValueError): transition_execution(h,"E","RUNNING")
    def test_append_only_history(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"h.jsonl"; create_execution(h,"E","S","H"); transition_execution(h,"E","RUNNING"); self.assertEqual(len(h.read_text().splitlines()),2)
    def test_metrics_and_checkpoint_metadata(self):
        with tempfile.TemporaryDirectory() as root:
            h=Path(root)/"h.jsonl"; create_execution(h,"E","S","H"); result=transition_execution(h,"E","RUNNING",{"loss":1.0},{"step":2}); self.assertEqual(result["metrics"],{"loss":1.0}); self.assertEqual(result["checkpoint"],{"step":2})

if __name__ == "__main__": unittest.main()
