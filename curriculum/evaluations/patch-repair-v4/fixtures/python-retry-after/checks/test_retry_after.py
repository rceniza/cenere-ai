import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from retry_after import parse_retry_after


class RetryAfterTests(unittest.TestCase):
    def test_valid_boundaries_and_whitespace(self):
        self.assertEqual(parse_retry_after("0"), 0)
        self.assertEqual(parse_retry_after(" 42\t"), 42)
        self.assertEqual(parse_retry_after("86400"), 86400)

    def test_invalid_values_return_none(self):
        for value in (None, "", " ", "-1", "+1", "1.0", "86401", "１２", "1x"):
            with self.subTest(value=value):
                self.assertIsNone(parse_retry_after(value))


if __name__ == "__main__":
    unittest.main()
