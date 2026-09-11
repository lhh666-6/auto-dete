import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_latest_manifest.py"


def load_module():
    spec = importlib.util.spec_from_file_location("build_latest_manifest", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ManifestBuilderTests(unittest.TestCase):
    def test_manifest_is_deterministic_and_excludes_build_artifacts(self):
        module = load_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "paper" / "out").mkdir(parents=True)
            (root / "tmp").mkdir()
            (root / ".hypothesis").mkdir()
            (root / "build").mkdir()
            (root / "package.egg-info").mkdir()
            (root / "README.md").write_bytes(b"latest\n")
            (root / "paper" / "main.pdf").write_bytes(b"main")
            (root / "paper" / "out" / "main.aux").write_text("aux")
            (root / "tmp" / "page.png").write_bytes(b"png")
            (root / ".hypothesis" / "state").write_text("state")
            (root / "build" / "wheel.bin").write_bytes(b"wheel")
            (root / "package.egg-info" / "PKG-INFO").write_text("metadata")
            (root / "MANIFEST-r27.json").write_text("old")

            manifest = module.build_manifest(
                root,
                pages={"main": 59, "supplement": 16},
                citations=54,
            )

            # Assert against the module's own revision so that a revision bump
            # cannot leave this test asserting a stale value.
            self.assertTrue(module.REVISION)
            self.assertEqual(manifest["revision"], module.REVISION)
            self.assertEqual(manifest["pages"], {"main": 59, "supplement": 16})
            self.assertEqual(
                list(manifest["files"]),
                ["README.md", "paper/main.pdf"],
            )
            self.assertEqual(
                manifest["files"]["README.md"]["sha256"],
                hashlib.sha256(b"latest\n").hexdigest(),
            )

            output = root / "MANIFEST-r27.json"
            module.write_manifest(output, manifest)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), manifest)
            self.assertEqual(module.verify_manifest(root, output), [])


if __name__ == "__main__":
    unittest.main()
