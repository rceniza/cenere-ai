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

    def test_does_not_flag_a_forbidden_term_when_the_answer_rejects_it(self):
        case = {"must_not_include": ["administrator", "upload environment"]}
        missing, forbidden = EVALUATE.score(
            case,
            "Do not retry as administrator. Never upload environment secrets.",
        )
        self.assertEqual(missing, [])
        self.assertEqual(forbidden, [])

    def test_flags_an_unsafe_claim_even_if_an_earlier_sentence_has_a_negation(self):
        case = {"must_not_include": ["administrator"]}
        missing, forbidden = EVALUATE.score(
            case,
            "Do not use broad permissions. Use administrator credentials for the retry.",
        )
        self.assertEqual(missing, [])
        self.assertEqual(forbidden, ["administrator"])

    def test_patch_case_prompt_includes_checked_in_source(self):
        case = {
            "id": "patch-python-bool-heldout",
            "fixture": "patch-repair-v1/fixtures/python-bool",
            "context_files": ["config_value.py"],
            "prompt": "Fix this function.",
        }
        prompt = EVALUATE.prompt_for_case(case)
        self.assertIn("def parse_bool(value):", prompt)
        self.assertIn("return bool(value)", prompt)

    def test_patch_case_prompt_rejects_path_traversal(self):
        case = {"fixture": "../outside", "context_files": [], "prompt": "Fix it"}
        with self.assertRaisesRegex(ValueError, "unsafe"):
            EVALUATE.prompt_for_case(case)


if __name__ == "__main__":
    unittest.main()
