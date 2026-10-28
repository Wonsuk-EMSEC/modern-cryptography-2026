"""Student package and environment checks; completion uses each Part's checker."""
import unittest
import hashlib
import json
from pathlib import Path
import shutil
import ssl


class MaterialsTests(unittest.TestCase):
    def test_eight_parts(self):
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(sorted(p.name for p in root.glob("part[0-9][0-9]") if p.is_dir()),
                         [f"part{i:02d}" for i in range(1, 9)])
        for number in range(1, 9):
            part = root / f"part{number:02d}"
            for relative in ("README.md", "tests/check.py"):
                self.assertTrue((part / relative).is_file(), f"missing {part / relative}")
            self.assertTrue(any((part / "starter").iterdir()))

    def test_course_tools(self):
        for tool in ("gcc", "openssl", "make"):
            self.assertIsNotNone(shutil.which(tool), tool)
        self.assertTrue(ssl.OPENSSL_VERSION)

    def test_release_data(self):
        root = Path(__file__).resolve().parents[1]
        recorded = json.loads((root / "data_manifest.json").read_text())
        for name, expected in recorded["sha256"].items():
            self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), expected, name)


if __name__ == "__main__":
    unittest.main()
