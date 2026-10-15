import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mean import mean


class MeanTests(unittest.TestCase):
    def test_average_returns_float(self):
        self.assertEqual(mean([1, 2, 6]), 3.0)
        self.assertEqual(mean([2, 3]), 2.5)

    def test_empty_input_has_defined_result(self):
        self.assertIsNone(mean([]))


if __name__ == "__main__":
    unittest.main()
