import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "train.py"
SPEC = importlib.util.spec_from_file_location("cenere_train", MODULE_PATH)
TRAIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TRAIN)
EVAL_SPEC = importlib.util.spec_from_file_location("cenere_evaluate", Path(__file__).resolve().parents[1] / "evaluate.py")
EVAL = importlib.util.module_from_spec(EVAL_SPEC)
EVAL_SPEC.loader.exec_module(EVAL)


class DatasetValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.data = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def write_rows(self, rows):
        (self.data / "train.jsonl").write_text("\n".join(rows) + "\n", encoding="utf-8")

    def row(self, prompt="Question", answer="Reviewed answer"):
        return json.dumps({"messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": answer},
        ]})

    def test_accepts_two_reviewed_chat_rows(self):
        self.write_rows([self.row(), self.row("Second", "Answer")])
        TRAIN.validate_dataset(self.data)

    def test_requires_two_examples(self):
        self.write_rows([self.row()])
        with self.assertRaisesRegex(SystemExit, "at least two"):
            TRAIN.validate_dataset(self.data)

    def test_rejects_malformed_json_and_message_shapes(self):
        self.write_rows(["{"])
        with self.assertRaisesRegex(SystemExit, "Invalid JSON"):
            TRAIN.validate_dataset(self.data)
        self.write_rows([json.dumps({"messages": ["not an object", {}]})])
        with self.assertRaisesRegex(SystemExit, "Each message must be an object"):
            TRAIN.validate_dataset(self.data)

    def test_rejects_blank_assistant_answer(self):
        self.write_rows([self.row(answer=" "), self.row()])
        with self.assertRaisesRegex(SystemExit, "non-empty assistant answer"):
            TRAIN.validate_dataset(self.data)

    def test_missing_dataset_has_actionable_error(self):
        with self.assertRaisesRegex(SystemExit, "prepare reviewed chat examples"):
            TRAIN.validate_dataset(self.data)

    def test_evaluation_rubric_accepts_equivalent_valid_rust_and_rejects_wrong_types(self):
        case = {
            "must_include_any": [["line.parse::<i64>()", "parse::<i64>"]],
            "must_not_include": ["parse::<i32>"],
        }
        self.assertEqual(EVAL.score(case, "line.parse::<i64>()"), ([], []))
        self.assertEqual(EVAL.score(case, "line.parse::<i32>()"), (["one of: line.parse::<i64>() | parse::<i64>"], ["parse::<i32>"]))


if __name__ == "__main__":
    unittest.main()
