#!/usr/bin/env python3
"""Add test-feedback patch examples to the problem-solving training split."""

import argparse
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "cenere-problem-solving-v6"
PREVIOUS = ROOT / "cenere-problem-solving-v5"
FIXTURES = ROOT.parent / "evaluations" / "patch-repair-v1" / "fixtures"
FENCE = chr(96) * 3

FEEDBACK = [
    {
        "id": "feedback-python-clamp-after-test-failure",
        "fixture": "train-python-clamp",
        "file": "percentage.py",
        "language": "python",
        "track": "python",
        "task": "The patch for clamp_percent passed an in-range test but failed the boundary tests below. Use the test output to fix the implementation. Preserve the signature and return only a fenced unified git diff.",
        "failure": "FAIL: clamp_percent(-3) returned -3; expected 0\nFAIL: clamp_percent(140) returned 140; expected 100",
        "fixed": "def clamp_percent(value):\n    return min(100, max(0, value))\n",
    },
    {
        "id": "feedback-javascript-retry-after-test-failure",
        "fixture": "train-js-retry",
        "file": "retry.js",
        "language": "javascript",
        "track": "javascript-typescript",
        "task": "The patch for shouldRetry(status) passed the server-error test but failed the cases below. Use the test output to correct the status policy. Preserve the export and return only a fenced unified git diff.",
        "failure": "AssertionError: shouldRetry(404) returned true; expected false\nAssertionError: shouldRetry(600) returned true; expected false",
        "fixed": "function shouldRetry(status) {\n  return status === 408 || status === 425 || status === 429 || (status >= 500 && status <= 599);\n}\n\nmodule.exports = { shouldRetry };\n",
    },
    {
        "id": "feedback-rust-checked-sum-after-test-failure",
        "fixture": "train-rust-sum",
        "file": "src/lib.rs",
        "language": "rust",
        "track": "rust",
        "task": "The patch for checked_sum passed ordinary inputs but failed the overflow test. Use the test output to fix it so signed 32-bit overflow returns None, while empty input returns Some(0). Preserve the signature and return only a fenced unified git diff.",
        "failure": "test overflow_returns_none ... FAILED\nassertion failed: checked_sum(&[i32::MAX, 1]).is_none()",
        "fixed": "pub fn checked_sum(values: &[i32]) -> Option<i32> {\n    values.iter().try_fold(0i32, |sum, value| sum.checked_add(*value))\n}\n",
    },
    {
        "id": "feedback-go-first-nonempty-after-test-failure",
        "fixture": "train-go-first-nonempty",
        "file": "strings.go",
        "language": "go",
        "track": "go-java",
        "task": "The patch for firstNonEmpty returned the first nonblank input but failed the whitespace case below. Use the test output to correct it. Preserve the signature and return only a fenced unified git diff.",
        "failure": "FAIL: TestFirstNonEmptyTrims\nstrings_test.go:12: got \"  alpha  \", want \"alpha\"",
        "fixed": "package patchtrain\n\nimport \"strings\"\n\nfunc firstNonEmpty(values []string) string {\n\tfor _, value := range values {\n\t\tif trimmed := strings.TrimSpace(value); trimmed != \"\" {\n\t\t\treturn trimmed\n\t\t}\n\t}\n\treturn \"\"\n}\n",
    },
]


def make_diff(relative: str, original: str, updated: str) -> str:
    body = "".join(difflib.unified_diff(
        original.splitlines(keepends=True), updated.splitlines(keepends=True),
        fromfile=f"a/{relative}", tofile=f"b/{relative}",
    ))
    return f"diff --git a/{relative} b/{relative}\n{body}"


def encode(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode()


def render() -> dict[str, bytes]:
    train = [json.loads(line) for line in (PREVIOUS / "train.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    for item in FEEDBACK:
        original = (FIXTURES / item["fixture"] / "files" / item["file"]).read_text(encoding="utf-8")
        prompt = (
            f"{item['task']}\n\nFailing test output:\n{FENCE}text\n{item['failure']}\n{FENCE}"
            f"\n\nSource file {item['file']}:\n{FENCE}{item['language']}\n{original}{FENCE}"
        )
        patch = make_diff(item["file"], original, item["fixed"])
        train.append({
            "id": item["id"], "track": item["track"], "level": "intermediate",
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": f"{FENCE}diff\n{patch}{FENCE}"},
            ],
        })
    all_rows = [
        json.loads(line)
        for name in ("valid.jsonl", "eval.jsonl")
        for line in (PREVIOUS / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    ids = [row["id"] for row in [*train, *all_rows]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate problem-solving v6 dataset IDs")
    return {
        "train.jsonl": encode(train),
        "valid.jsonl": (PREVIOUS / "valid.jsonl").read_bytes(),
        "eval.jsonl": (PREVIOUS / "eval.jsonl").read_bytes(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    if args.check:
        stale = [name for name, data in outputs.items() if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if stale:
            raise SystemExit("Problem-solving v6 dataset is stale: " + ", ".join(stale))
        print("Problem-solving v6 dataset matches its curated source.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    print(
        f"Wrote {len(outputs['train.jsonl'].splitlines())} training rows and preserved "
        "validation/evaluation splits with four test-feedback repairs."
    )


if __name__ == "__main__":
    main()
