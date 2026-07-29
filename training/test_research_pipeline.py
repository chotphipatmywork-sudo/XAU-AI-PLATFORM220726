import json
import tempfile
import unittest
from pathlib import Path

try:
    from .research_pipeline import build_dataset, register_source, validate_dataset
except ImportError:
    from research_pipeline import build_dataset, register_source, validate_dataset


class ResearchPipelineTests(unittest.TestCase):
    def make_source(self, root: Path) -> Path:
        source = root / "source.csv"
        source.write_text(
            "record_id,symbol,timestamp\n"
            "2,XAUUSD,2024-01-02\n"
            "1,XAUUSD,2024-01-01\n",
            encoding="utf-8",
        )
        return source

    def register(self, source: Path):
        return register_source(
            source,
            source_id="SRC-TEST",
            source_version="1.0.0",
            schema_version="1.0.0",
            provider="test",
            symbol="XAUUSD",
            timeframe="M5",
            timezone="UTC",
        )

    def test_source_registration(self):
        with tempfile.TemporaryDirectory() as temporary:
            registration = self.register(self.make_source(Path(temporary)))
            self.assertEqual(registration.record_count, 2)
            self.assertTrue(registration.sha256)

    def test_generation_and_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.make_source(root)
            output, manifest = root / "dataset.csv", root / "manifest.json"
            build_dataset(source, output, manifest, self.register(source))
            self.assertTrue(output.read_text(encoding="utf-8").splitlines()[1].startswith("1,"))
            self.assertFalse(json.loads(manifest.read_text(encoding="utf-8"))["labels_generated"])

    def test_validation_rejects_duplicate(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            dataset, manifest = root / "dataset.csv", root / "manifest.json"
            dataset.write_text(
                "record_id,symbol,timestamp\n"
                "1,XAUUSD,2024-01-01\n"
                "1,XAUUSD,2024-01-02\n",
                encoding="utf-8",
            )
            manifest.write_text(
                json.dumps({"identity": {}, "dataset_path": "x", "dataset_sha256": "x", "manifest_version": "1.0.0"}),
                encoding="utf-8",
            )
            self.assertIn("duplicate record identity", validate_dataset(dataset, manifest))


if __name__ == "__main__":
    unittest.main()
