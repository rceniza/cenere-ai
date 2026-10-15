#!/usr/bin/env python3
"""Add executable patch-repair examples to the advanced problem-solving curriculum."""

import argparse
import difflib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "cenere-problem-solving-v3"
OUT = ROOT / "cenere-problem-solving-v4"
FIXTURES = ROOT.parent / "evaluations"

PATCHES = [
    {
        "id": "repair-python-clamp-percent",
        "track": "python",
        "level": "intermediate",
        "fixture": "patch-repair-v1/fixtures/train-python-clamp",
        "file": "percentage.py",
        "language": "python",
        "task": "Fix `clamp_percent` so it clamps integer percentages to the inclusive range 0 through 100 while preserving values already in range. Return only a fenced unified git diff.",
        "checks": [["python3", "-m", "unittest", "discover", "-s", "checks", "-p", "test*.py"]],
    },
    {
        "id": "repair-javascript-retry-status",
        "track": "javascript-typescript",
        "level": "intermediate",
        "fixture": "patch-repair-v1/fixtures/train-js-retry",
        "file": "retry.js",
        "language": "javascript",
        "task": "Fix `shouldRetry(status)` so it returns true only for HTTP 408, 425, 429, and 500 through 599. Return false for success, redirects, other 4xx, and all other values in the tests. Preserve the exported function. Return only a fenced unified git diff.",
        "checks": [["node", "checks/hidden.js"]],
    },
    {
        "id": "repair-rust-checked-sum",
        "track": "rust",
        "level": "intermediate",
        "fixture": "patch-repair-v1/fixtures/train-rust-sum",
        "file": "src/lib.rs",
        "language": "rust",
        "task": "Fix `checked_sum` to return the sum as `Some`, return `Some(0)` for an empty slice, and return `None` if signed 32-bit addition overflows. Preserve the public signature and use only the standard library. Return only a fenced unified git diff.",
        "checks": [["rustc", "--edition=2021", "--test", "checks/hidden.rs", "-o", "checks/hidden-tests"], ["checks/hidden-tests"]],
    },
]

FIXED = {
    "repair-python-clamp-percent": '''def clamp_percent(value):
    return min(100, max(0, value))
''',
    "repair-javascript-retry-status": '''function shouldRetry(status) {
  return status === 408 || status === 425 || status === 429 || (status >= 500 && status <= 599);
}

module.exports = { shouldRetry };
''',
    "repair-rust-checked-sum": '''pub fn checked_sum(values: &[i32]) -> Option<i32> {
    values.iter().try_fold(0i32, |sum, value| sum.checked_add(*value))
}
''',
}


def read_rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (BASE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def encode(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode()


def make_diff(relative: str, original: str, updated: str) -> str:
    body = "".join(difflib.unified_diff(
        original.splitlines(keepends=True), updated.splitlines(keepends=True),
        fromfile=f"a/{relative}", tofile=f"b/{relative}",
    ))
    return f"diff --git a/{relative} b/{relative}\n{body}"


def render() -> dict[str, bytes]:
    train, valid, evaluation = (read_rows(name) for name in ("train.jsonl", "valid.jsonl", "eval.jsonl"))
    for item in PATCHES:
        relative = item["file"]
        source_path = FIXTURES / item["fixture"] / "files" / relative
        original = source_path.read_text(encoding="utf-8")
        prompt = item["task"] + f"\n\nSource file `{relative}`:\n```{item['language']}\n{original}```"
        patch = make_diff(relative, original, FIXED[item["id"]])
        train.append({"id": item["id"], "track": item["track"], "level": item["level"],
                      "messages": [{"role": "user", "content": prompt},
                                   {"role": "assistant", "content": f"```diff\n{patch}```"}]})
    ids = [row["id"] for rows in (train, valid, evaluation) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate problem-solving v4 dataset IDs")
    train_prompts = {row["messages"][0]["content"] for row in train}
    valid_prompts = {row["messages"][0]["content"] for row in valid}
    eval_prompts = {row["prompt"] for row in evaluation}
    if train_prompts & valid_prompts or train_prompts & eval_prompts or valid_prompts & eval_prompts:
        raise ValueError("problem-solving v4 prompts overlap splits")
    return {"train.jsonl": encode(train), "valid.jsonl": encode(valid), "eval.jsonl": encode(evaluation)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    if args.check:
        stale = [name for name, data in outputs.items() if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if stale:
            raise SystemExit("Problem-solving v4 dataset is stale: " + ", ".join(stale))
        print("Problem-solving v4 dataset matches its curated source.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    print(f"Wrote {len(outputs['train.jsonl'].splitlines())} training, {len(outputs['valid.jsonl'].splitlines())} validation, and {len(outputs['eval.jsonl'].splitlines())} held-out rubric rows.")


if __name__ == "__main__":
    main()
