import importlib.util
import json
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "curriculum/datasets/cenere-multistack-v1"
DATA_V2 = ROOT / "curriculum/datasets/cenere-multistack-v2"
DATA_V3 = ROOT / "curriculum/datasets/cenere-multistack-v3"
DATA_V4 = ROOT / "curriculum/datasets/cenere-multistack-v4"
DATA_PROBLEM = ROOT / "curriculum/datasets/cenere-problem-solving-v1"
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
SPEC_CODE_EVAL = importlib.util.spec_from_file_location("evaluate_code", ROOT / "training/evaluate_code.py")
CODE_EVAL = importlib.util.module_from_spec(SPEC_CODE_EVAL)
SPEC_CODE_EVAL.loader.exec_module(CODE_EVAL)
SPEC_V3 = importlib.util.spec_from_file_location("multistack_v3", ROOT / "curriculum/datasets/build_multistack_v3.py")
BUILDER_V3 = importlib.util.module_from_spec(SPEC_V3)
SPEC_V3.loader.exec_module(BUILDER_V3)
SPEC_V4 = importlib.util.spec_from_file_location("multistack_v4", ROOT / "curriculum/datasets/build_multistack_v4.py")
BUILDER_V4 = importlib.util.module_from_spec(SPEC_V4)
SPEC_V4.loader.exec_module(BUILDER_V4)
SPEC_PROBLEM = importlib.util.spec_from_file_location("problem_solving_v1", ROOT / "curriculum/datasets/build_problem_solving_v1.py")
BUILDER_PROBLEM = importlib.util.module_from_spec(SPEC_PROBLEM)
SPEC_PROBLEM.loader.exec_module(BUILDER_PROBLEM)


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def java_runtime_available():
    java = shutil.which("java")
    if java is None:
        return False
    try:
        return subprocess.run([java, "-version"], capture_output=True, timeout=5).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


class MultistackDatasetTests(unittest.TestCase):
    def test_problem_solving_dataset_is_reproducible_and_split_safe(self):
        rendered = BUILDER_PROBLEM.render()
        for filename, content in rendered.items():
            self.assertEqual((DATA_PROBLEM / filename).read_bytes(), content, filename)
        train = read_jsonl(DATA_PROBLEM / "train.jsonl")
        valid = read_jsonl(DATA_PROBLEM / "valid.jsonl")
        evaluation = read_jsonl(DATA_PROBLEM / "eval.jsonl")
        self.assertEqual((len(train), len(valid), len(evaluation)), (163, 53, 69))
        self.assertEqual(sum(row["track"] == "problem-solving" for row in train), 12)
        self.assertEqual(sum(row["track"] == "problem-solving" for row in valid), 6)
        self.assertEqual(sum(row["track"] == "problem-solving" for row in evaluation), 10)
        train_prompts = {row["messages"][0]["content"] for row in train}
        valid_prompts = {row["messages"][0]["content"] for row in valid}
        eval_prompts = {row["prompt"] for row in evaluation}
        self.assertFalse(train_prompts & valid_prompts)
        self.assertFalse(train_prompts & eval_prompts)
        self.assertFalse(valid_prompts & eval_prompts)

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
        tracks = {track["id"] for track in json.loads((ROOT / "curriculum/catalog.json").read_text())["tracks"]}
        train = {row["messages"][0]["content"] for row in read_jsonl(DATA / "train.jsonl")}
        valid_rows = read_jsonl(DATA / "valid.jsonl")
        valid = {row["messages"][0]["content"] for row in valid_rows}
        self.assertEqual(len(valid_rows), len(tracks))
        self.assertFalse(train & valid)

    def test_rubric_eval_has_coverage_for_all_tracks_and_nonempty_checks(self):
        rows = read_jsonl(DATA / "eval.jsonl")
        catalog_tracks = {track["id"] for track in json.loads((ROOT / "curriculum/catalog.json").read_text())["tracks"]}
        self.assertEqual(len(rows), len(catalog_tracks))
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
        self.assertEqual(len(train), len(json.loads((ROOT / "curriculum/catalog.json").read_text())["tracks"]) * 3 + 11)
        code_rows = [row for row in train if row["id"].endswith("-code")]
        self.assertEqual(len(code_rows), 11)
        self.assertEqual(
            {row["track"] for row in code_rows},
            {"c", "cpp", "php", "javascript-typescript", "nodejs", "python", "rust", "go-java", "csharp"},
        )
        source_by_id = {
            f"{track}-beginner-normalize-list-{fence.lower()}-code": (source, fence)
            for track, _display, source, fence in BUILDER_V2.EXAMPLES
        }
        for row in code_rows:
            answer = row["messages"][-1]["content"]
            source_rel, fence = source_by_id[row["id"]]
            source = (ROOT / "curriculum/examples/polyglot" / source_rel).read_text().rstrip()
            expected = f"```{fence}\n{source}\n```"
            self.assertEqual(answer, expected)

    def test_code_focused_training_stays_separate_from_heldout_rubric(self):
        train = {row["messages"][0]["content"] for row in read_jsonl(DATA_V2 / "train.jsonl")}
        valid = {row["messages"][0]["content"] for row in read_jsonl(DATA_V2 / "valid.jsonl")}
        evaluation = {row["prompt"] for row in read_jsonl(DATA_V2 / "eval.jsonl")}
        self.assertFalse(train & valid)
        self.assertFalse(train & evaluation)

    def test_code_execution_eval_is_held_out_and_covers_checked_stacks(self):
        train = {row["messages"][0]["content"] for row in read_jsonl(DATA_V2 / "train.jsonl")}
        code_eval = read_jsonl(DATA_V2 / "code-eval.jsonl")
        self.assertEqual(len(code_eval), 11)
        self.assertEqual(len({row["id"] for row in code_eval}), len(code_eval))
        self.assertEqual(
            {row["language"] for row in code_eval},
            {"c", "cpp", "php", "javascript", "typescript", "nodejs", "python", "rust", "go", "java", "csharp"},
        )
        self.assertTrue(all(row["prompt"] not in train for row in code_eval))
        self.assertTrue(all("return only" in row["prompt"].lower() for row in code_eval))

    def test_code_evaluator_extracts_fenced_sources_and_rejects_missing_code(self):
        self.assertEqual(CODE_EVAL.fenced_code("```python\nprint('ok')\n```", "python"), "print('ok')")
        self.assertIsNone(CODE_EVAL.fenced_code("I cannot provide code.", "python"))
        self.assertIsNone(CODE_EVAL.fenced_code("```bash\necho wrong language\n```", "python"))

    def test_typescript_reference_passes_the_held_out_code_evaluator(self):
        source = (ROOT / "curriculum/examples/polyglot/typescript/main.ts").read_text()
        failures = CODE_EVAL.check({"language": "typescript"}, f"```typescript\n{source}\n```")
        self.assertEqual(failures, [])

    @unittest.skipUnless(java_runtime_available(), "Java runtime is not installed")
    def test_java_reference_passes_the_held_out_code_evaluator(self):
        source = (ROOT / "curriculum/examples/polyglot/java/Main.java").read_text()
        failures = CODE_EVAL.check({"language": "java"}, f"```java\n{source}\n```")
        self.assertEqual(failures, [])

    def test_csharp_normalizer_reference_passes_the_held_out_code_evaluator(self):
        source = (ROOT / "curriculum/examples/polyglot/csharp/main.cs").read_text()
        failures = CODE_EVAL.check({"language": "csharp"}, f"```csharp\n{source}\n```")
        if failures == ["toolchain unavailable: dotnet"]:
            self.skipTest(".NET SDK is not installed")
        self.assertEqual(failures, [])

    def test_ecosystem_dataset_is_reproducible_split_safe_and_covers_all_new_tracks(self):
        rendered = BUILDER_V3.render()
        for filename, content in rendered.items():
            self.assertEqual((DATA_V3 / filename).read_bytes(), content, filename)
        train = read_jsonl(DATA_V3 / "train.jsonl")
        valid = read_jsonl(DATA_V3 / "valid.jsonl")
        evaluation = read_jsonl(DATA_V3 / "eval.jsonl")
        self.assertEqual(len(train), 93 + len(BUILDER_V2.EXAMPLES) + len(BUILDER_V3.TRAIN))
        self.assertEqual(len(valid), 31 + len(BUILDER_V3.VALID))
        self.assertEqual(len(evaluation), 31 + len(BUILDER_V3.EVAL))
        self.assertEqual({row["track"] for row in train if row["id"].startswith("ecosystem-")},
                         {"frontend-frameworks", "backend-frameworks", "legacy-systems", "database-engines", "mobile-desktop", "build-toolchains"})
        train_prompts = {row["messages"][0]["content"] for row in train}
        valid_prompts = {row["messages"][0]["content"] for row in valid}
        eval_prompts = {row["prompt"] for row in evaluation}
        self.assertFalse(train_prompts & valid_prompts)
        self.assertFalse(train_prompts & eval_prompts)
        self.assertFalse(valid_prompts & eval_prompts)

    def test_correction_dataset_is_reproducible_and_keeps_code_evaluation_held_out(self):
        rendered = BUILDER_V4.render()
        for filename, content in rendered.items():
            self.assertEqual((DATA_V4 / filename).read_bytes(), content, filename)
        train = read_jsonl(DATA_V4 / "train.jsonl")
        valid = read_jsonl(DATA_V4 / "valid.jsonl")
        evaluation = read_jsonl(DATA_V4 / "eval.jsonl")
        code_eval = read_jsonl(DATA_V4 / "code-eval.jsonl")
        self.assertEqual(len(train), 151)
        self.assertEqual(len(valid), 47)
        self.assertEqual(len(evaluation), 59)
        self.assertEqual(len(code_eval), 22)
        train_prompts = {row["messages"][0]["content"] for row in train}
        self.assertFalse(train_prompts & {row["messages"][0]["content"] for row in valid})
        self.assertFalse(train_prompts & {row["prompt"] for row in evaluation})
        self.assertFalse(train_prompts & {row["prompt"] for row in code_eval})
        sum_rows = [row for row in code_eval if row.get("exercise") == "sum-int32"]
        self.assertEqual(len(sum_rows), 11)
        self.assertEqual({row["language"] for row in sum_rows},
                         {"c", "cpp", "php", "javascript", "typescript", "nodejs", "python", "rust", "go", "java", "csharp"})

    def test_sum_int32_reference_programs_pass_executable_evaluator(self):
        sources = {
            "c": ("c/sum_int32.c", "c"), "cpp": ("cpp/sum_int32.cpp", "cpp"),
            "php": ("php/sum_int32.php", "php"), "javascript": ("node/sum_int32.js", "javascript"),
            "typescript": ("typescript/sum_int32.ts", "typescript"), "nodejs": ("node/sum_int32.js", "javascript"),
            "python": ("python/sum_int32.py", "python"), "rust": ("rust/sum_int32.rs", "rust"),
            "go": ("go/sum_int32.go", "go"), "java": ("java/SumInt32.java", "java"),
            "csharp": ("csharp/sum_int32.cs", "csharp"),
        }
        for language, (relative, fence) in sources.items():
            with self.subTest(language=language):
                answer = f"```{fence}\n{(ROOT / 'curriculum/examples/polyglot' / relative).read_text()}\n```"
                failures = CODE_EVAL.check({"language": language, "exercise": "sum-int32"}, answer)
                if language == "csharp" and failures == ["toolchain unavailable: dotnet"]:
                    self.skipTest(".NET SDK is not installed")
                if language == "java" and failures == ["toolchain unavailable: java runtime"]:
                    self.skipTest("Java runtime is not installed")
                if language == "csharp" and failures == ["toolchain unavailable: dotnet"]:
                    self.skipTest(".NET SDK is not installed")
                self.assertEqual(failures, [])

    def test_csharp_compile_failures_include_compiler_diagnostics(self):
        failures = CODE_EVAL.check(
            {"language": "csharp", "exercise": "sum-int32"},
            "```csharp\nnot valid C#;\n```",
        )
        if failures == ["toolchain unavailable: dotnet"]:
            self.skipTest(".NET SDK is not installed")
        self.assertIn("compile failed", failures[0])
        self.assertIn("error CS", failures[0])

    def test_new_ecosystem_tracks_link_to_official_documentation(self):
        catalog = json.loads((ROOT / "curriculum/catalog.json").read_text())
        tracks = {track["id"]: track for track in catalog["tracks"]}
        expected = {"frontend-frameworks", "backend-frameworks", "legacy-systems", "database-engines", "mobile-desktop", "build-toolchains"}
        self.assertTrue(expected <= tracks.keys())
        for track_id in expected:
            self.assertTrue(tracks[track_id]["references"], track_id)
            self.assertTrue(all(ref["url"].startswith("https://") for ref in tracks[track_id]["references"]))


if __name__ == "__main__":
    unittest.main()
