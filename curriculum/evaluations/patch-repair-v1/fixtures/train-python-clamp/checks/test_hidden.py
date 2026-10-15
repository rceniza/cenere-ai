import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from percentage import clamp_percent


class ClampPercentTests(unittest.TestCase):
    def test_clamps_both_bounds_and_preserves_in_range_values(self):
        self.assertEqual(clamp_percent(-1), 0)
        self.assertEqual(clamp_percent(0), 0)
        self.assertEqual(clamp_percent(45), 45)
        self.assertEqual(clamp_percent(100), 100)
        self.assertEqual(clamp_percent(101), 100)


if __name__ == "__main__":
    unittest.main()
