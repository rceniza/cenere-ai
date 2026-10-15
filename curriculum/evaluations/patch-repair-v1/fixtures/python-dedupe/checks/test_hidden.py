import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dedupe import first_by_id


class FirstByIdTests(unittest.TestCase):
    def test_preserves_first_occurrence_order_and_value(self):
        a, b, later_a = {"id": "a", "v": 1}, {"id": "b", "v": 2}, {"id": "a", "v": 9}
        self.assertEqual(first_by_id([a, b, later_a]), [a, b])

    def test_handles_empty_and_missing_id(self):
        self.assertEqual(first_by_id([]), [])
        with self.assertRaises(KeyError):
            first_by_id([{"v": 1}])


if __name__ == "__main__":
    unittest.main()
