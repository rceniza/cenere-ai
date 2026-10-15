import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "cenere_evaluate", Path(__file__).resolve().parents[1] / "evaluate.py"
)
EVALUATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVALUATE)


class RubricTests(unittest.TestCase):
    def test_accepts_any_alternative_in_each_required_group(self):
        case = {
            "must_include_any": [["readiness", "traffic"], ["restart", "liveness"]],
            "must_not_include": ["always restart"],
        }
        missing, forbidden = EVALUATE.score(case, "Readiness controls traffic; liveness can restart a stuck container.")
        self.assertEqual(missing, [])
        self.assertEqual(forbidden, [])

    def test_rejects_missing_requirements_and_forbidden_claims(self):
        case = {"must_include": ["offset"], "must_not_include": ["commit before writing"]}
        missing, forbidden = EVALUATE.score(case, "Commit before writing the database row.")
        self.assertEqual(missing, ["offset"])
        self.assertEqual(forbidden, ["commit before writing"])


if __name__ == "__main__":
    unittest.main()
