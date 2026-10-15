import difflib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("cenere_evaluate_patch", ROOT / "training/evaluate_patch.py")
PATCH_EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PATCH_EVAL)
CASES = [json.loads(line) for line in (ROOT / "curriculum/evaluations/patch-repair-v1/cases.jsonl").read_text().splitlines()]
CASES_V2 = [json.loads(line) for line in (ROOT / "curriculum/evaluations/patch-repair-v2/cases.jsonl").read_text().splitlines()]
CASES_V3 = [json.loads(line) for line in (ROOT / "curriculum/evaluations/patch-repair-v3/cases.jsonl").read_text().splitlines()]


class PatchEvaluationTests(unittest.TestCase):
    def test_reference_patches_apply_and_pass_hidden_behavior_checks(self):
        expected = {
            "patch-python-bool-heldout": ("config_value.py", '''def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "1", "on"}:
            return True
        if normalized in {"false", "no", "0", "off"}:
            return False
    raise ValueError("invalid boolean value")
'''),
            "patch-python-port-heldout": ("port.py", '''def parse_port(value):
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text.isascii() or not text.isdecimal():
        return None
    port = int(text)
    return port if 1 <= port <= 65535 else None
'''),
            "patch-rust-dedupe-heldout": ("src/lib.rs", '''pub fn unique_sorted(values: &[i32]) -> Vec<i32> {
    let mut result = values.to_vec();
    result.sort();
    result.dedup();
    result
}
'''),
            "patch-python-dedupe-heldout": ("dedupe.py", '''def first_by_id(rows):
    result = []
    seen = set()
    for row in rows:
        key = row["id"]
        if key not in seen:
            seen.add(key)
            result.append(row)
    return result
'''),
        }
        for case in CASES:
            with self.subTest(case=case["id"]):
                path, new = expected[case["id"]]
                old = (PATCH_EVAL.FIXTURE_ROOT / case["fixture"] / "files" / path).read_text()
                body = "".join(difflib.unified_diff(
                    old.splitlines(keepends=True), new.splitlines(keepends=True),
                    fromfile="a/" + path, tofile="b/" + path,
                ))
                answer = f"```diff\ndiff --git a/{path} b/{path}\n{body}```"
                self.assertEqual(PATCH_EVAL.check(case, answer), [])

    def test_rejects_unsafe_fixture_paths(self):
        self.assertIn("unsafe fixture path", PATCH_EVAL.check({"fixture": "../escape"}, "diff")[0])

    def test_patch_repair_v2_reference_fixes_pass_hidden_behavior_checks(self):
        expected = {
            "patch-v2-python-mean-heldout": ("mean.py", '''def mean(values):
    if not values:
        return None
    return sum(values) / len(values)
'''),
            "patch-v2-javascript-origin-heldout": ("redirect.js", '''function isTrustedRedirect(raw) {
  try {
    return new URL(raw).origin === "https://trusted.example";
  } catch {
    return false;
  }
}

module.exports = { isTrustedRedirect };
'''),
            "patch-v2-rust-insert-heldout": ("src/lib.rs", '''pub fn insert_sorted_unique(values: &[i32], value: i32) -> Vec<i32> {
    let mut result = values.to_vec();
    result.push(value);
    result.sort();
    result.dedup();
    result
}
'''),
        }
        for case in CASES_V2:
            with self.subTest(case=case["id"]):
                path, new = expected[case["id"]]
                old = (PATCH_EVAL.FIXTURE_ROOT / case["fixture"] / "files" / path).read_text()
                body = "".join(difflib.unified_diff(
                    old.splitlines(keepends=True), new.splitlines(keepends=True),
                    fromfile="a/" + path, tofile="b/" + path,
                ))
                answer = f"```diff\ndiff --git a/{path} b/{path}\n{body}```"
                self.assertEqual(PATCH_EVAL.check(case, answer), [])

    def test_requires_a_diff(self):
        self.assertEqual(PATCH_EVAL.check(CASES[0], "No code changes needed."), ["missing unified diff"])

    def test_accepts_standard_unified_headers_with_model_annotations(self):
        path = "mean.py"
        original = (PATCH_EVAL.FIXTURE_ROOT / CASES_V2[0]["fixture"] / "files" / path).read_text()
        updated = "def mean(values):\n    if not values:\n        return None\n    return sum(values) / len(values)\n"
        body = "".join(difflib.unified_diff(
            original.splitlines(keepends=True), updated.splitlines(keepends=True),
            fromfile=path, tofile=path,
        )).replace(f"--- {path}\n", f"--- {path} ---\n", 1).replace(
            f"+++ {path}\n", f"+++ {path} ---\n", 1
        )
        answer = f"```diff\n{body}```"
        self.assertEqual(PATCH_EVAL.check(CASES_V2[0], answer), [])

    def test_patch_repair_v3_go_and_csharp_reference_fixes_pass(self):
        expected = {
            "patch-v3-go-retries-heldout": ("retries.go", '''package main

func clampRetries(value int) int {
    if value < 1 {
        return 1
    }
    if value > 10 {
        return 10
    }
    return value
}
'''),
            "patch-v3-csharp-port-heldout": ("NetworkRules.cs", '''public static class NetworkRules
{
    public static bool IsValidPort(int port)
    {
        return port >= 1 && port <= 65535;
    }
}
'''),
        }
        for case in CASES_V3:
            with self.subTest(case=case["id"]):
                path, new = expected[case["id"]]
                old = (PATCH_EVAL.FIXTURE_ROOT / case["fixture"] / "files" / path).read_text()
                body = "".join(difflib.unified_diff(
                    old.splitlines(keepends=True), new.splitlines(keepends=True),
                    fromfile="a/" + path, tofile="b/" + path,
                ))
                answer = f"```diff\ndiff --git a/{path} b/{path}\n{body}```"
                self.assertEqual(PATCH_EVAL.check(case, answer), [])


if __name__ == "__main__":
    unittest.main()
