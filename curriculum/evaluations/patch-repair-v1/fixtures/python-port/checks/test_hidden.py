import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from port import parse_port


class ParsePortTests(unittest.TestCase):
    def test_valid_boundaries_and_whitespace(self):
        self.assertEqual(parse_port("1"), 1)
        self.assertEqual(parse_port(" 443 "), 443)
        self.assertEqual(parse_port("65535"), 65535)

    def test_invalid_range_and_non_decimal_values(self):
        for value in ("0", "65536", "-1", "+80", "80x", "8.0", "", True, None):
            with self.subTest(value=value):
                self.assertIsNone(parse_port(value))


if __name__ == "__main__":
    unittest.main()
