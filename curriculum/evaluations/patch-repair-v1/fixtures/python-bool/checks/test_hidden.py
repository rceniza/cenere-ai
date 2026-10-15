import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config_value import parse_bool


class ParseBoolTests(unittest.TestCase):
    def test_boolean_inputs(self):
        self.assertIs(parse_bool(True), True)
        self.assertIs(parse_bool(False), False)

    def test_supported_text_values(self):
        for value in ("true", "TRUE", " yes ", "1", "on"):
            self.assertIs(parse_bool(value), True, value)
        for value in ("false", "FALSE", " no ", "0", "off"):
            self.assertIs(parse_bool(value), False, value)

    def test_unknown_values_are_rejected(self):
        for value in ("maybe", "", "2", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                parse_bool(value)


if __name__ == "__main__":
    unittest.main()
