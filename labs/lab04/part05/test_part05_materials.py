"""Check that the distributed sample files are present and readable."""

from pathlib import Path
import unittest


DATA = Path(__file__).resolve().parent / "data"


class PublicChallengeTests(unittest.TestCase):
    def test_sample_files(self):
        paths = sorted(DATA.glob("sample_*.bin"))
        self.assertEqual(len(paths), 12)
        self.assertEqual([path.name for path in paths],
                         [f"sample_{number:02d}.bin" for number in range(12)])
        contents = [path.read_bytes() for path in paths]
        self.assertTrue(all(len(payload) == len(contents[0]) for payload in contents))
        self.assertTrue(all(contents))
        self.assertEqual(len(set(contents)), len(contents))


if __name__ == "__main__":
    unittest.main()
