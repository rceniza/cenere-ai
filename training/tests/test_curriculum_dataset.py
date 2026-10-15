import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "curriculum/datasets/cenere-multistack-v1"
DATA_V2 = ROOT / "curriculum/datasets/cenere-multistack-v2"
SPEC = importlib.util.spec_from_file_location(
    "multistack_v1", ROOT / "curriculum/datasets/build_multistack_v1.py"
)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)
SPEC_V2 = importlib.util.spec_from_file_location(
    "multistack_v2", ROOT / "curriculum/datasets/build_multistack_v2.py"
)
BUILDER_V2 = importlib.util.module_from_spec(SPEC_V2)
SPEC_V2.loader.exec_module(BUILDER_V2)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class MultistackDatasetTests(unittest.TestCase):
    def test_committed_data_matches_curated_source(self):
        rendered = BUILDER.render()
        for filename, content in rendered.items():
            self.assertEqual((DATA / filename).read_bytes(), content, filename)

    def test_training_covers_each_catalog_track_at_each_stage(self):
        tracks = {track["id"] for track in json.loads((ROOT / "curriculum/catalog.json").read_text())["tracks"]}
        rows = read_jsonl(DATA / "train.jsonl")
        self.assertEqual(len(rows), len(tracks) * 3)
        self.assertEqual({row["track"] for row in rows}, tracks)
        self.assertEqual(
            {(row["track"], row["level"]) for row in rows},
            {(track, level) for track in tracks for level in ("beginner", "intermediate", "advanced")},
        )
        self.assertTrue(all(row["messages"][-1]["role"] == "assistant" for row in rows))

    def test_train_and_validation_prompts_do_not_overlap(self):
        train = {row["messages"][0]["content"] for row in read_jsonl(DATA / "train.jsonl")}
        valid_rows = read_jsonl(DATA / "valid.jsonl")
        valid = {row["messages"][0]["content"] for row in valid_rows}
        self.assertEqual(len(valid_rows), 25)
        self.assertFalse(train & valid)

    def test_rubric_eval_has_coverage_for_all_tracks_and_nonempty_checks(self):
        rows = read_jsonl(DATA / "eval.jsonl")
        self.assertEqual(len(rows), 25)
        self.assertEqual({row["track"] for row in rows}, {item[0] for item in BUILDER.TRACKS})
        for row in rows:
            self.assertTrue(row["prompt"].strip())
            self.assertTrue(row["must_include_any"])
            self.assertTrue(all(group and all(term.strip() for term in group) for group in row["must_include_any"]))

    def test_code_focused_data_is_reproducible_and_uses_checked_references(self):
        rendered = BUILDER_V2.render()
        for filename, content in rendered.items():
            self.assertEqual((DATA_V2 / filename).read_bytes(), content, filename)
        train = read_jsonl(DATA_V2 / "train.jsonl")
        self.assertEqual(len(train), 83)
        code_rows = [row for row in train if row["id"].endswith("normalize-list-code")]
        self.assertEqual(len(code_rows), 8)
        self.assertEqual(
            {row["track"] for row in code_rows},
            {"c", "cpp", "php", "javascript-typescript", "nodejs", "python", "rust", "go-java"},
        )
        source_by_track = {track: source for track, _display, source, _fence in BUILDER_V2.EXAMPLES}
        fence_by_track = {track: fence for track, _display, _source, fence in BUILDER_V2.EXAMPLES}
        for row in code_rows:
            answer = row["messages"][-1]["content"]
            source = (ROOT / "curriculum/examples/polyglot" / source_by_track[row["track"]]).read_text().rstrip()
            expected = f"```{fence_by_track[row['track']]}\n{source}\n```"
            self.assertEqual(answer, expected)

    def test_code_focused_training_stays_separate_from_heldout_rubric(self):
        train = {row["messages"][0]["content"] for row in read_jsonl(DATA_V2 / "train.jsonl")}
        valid = {row["messages"][0]["content"] for row in read_jsonl(DATA_V2 / "valid.jsonl")}
        evaluation = {row["prompt"] for row in read_jsonl(DATA_V2 / "eval.jsonl")}
        self.assertFalse(train & valid)
        self.assertFalse(train & evaluation)


if __name__ == "__main__":
    unittest.main()
