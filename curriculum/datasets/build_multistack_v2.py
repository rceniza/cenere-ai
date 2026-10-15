#!/usr/bin/env python3
"""Add locally checked, code-producing examples to the multistack seed."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent / "cenere-multistack-v1"
OUT = Path(__file__).resolve().parent / "cenere-multistack-v2"
EXAMPLES = [
    ("c", "C", "c/main.c", "C"),
    ("cpp", "C++", "cpp/main.cpp", "C++"),
    ("php", "PHP", "php/main.php", "PHP"),
    ("javascript-typescript", "JavaScript", "node/main.js", "JavaScript"),
    ("javascript-typescript", "TypeScript", "typescript/main.ts", "typescript"),
    ("nodejs", "Node.js", "node/main.js", "JavaScript"),
    ("python", "Python", "python/main.py", "Python"),
    ("rust", "Rust", "rust/main.rs", "Rust"),
    ("go-java", "Go", "go/main.go", "Go"),
]
CODE_EVAL = [
    ("c", "C", "c"),
    ("cpp", "C++", "cpp"),
    ("php", "PHP", "php"),
    ("javascript-typescript", "JavaScript", "javascript"),
    ("javascript-typescript", "TypeScript", "typescript"),
    ("nodejs", "Node.js", "nodejs"),
    ("python", "Python", "python"),
    ("rust", "Rust", "rust"),
    ("go-java", "Go", "go"),
]


def lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def render() -> dict[str, bytes]:
    train = lines(BASE / "train.jsonl")
    track_count = len(json.loads((ROOT / "curriculum/catalog.json").read_text(encoding="utf-8"))["tracks"])
    require(len(train) == track_count * 3, "v1 training seed must contain three examples per track")
    ids = {row["id"] for row in train}
    for track, display, source_rel, fence in EXAMPLES:
        prompt = (
            f"Write a complete {display} command-line program that reads one comma-separated line of signed 32-bit integers, "
            "prints a JSON array sorted ascending with duplicates removed, prints [] for empty input, and exits non-zero "
            "without standard output for malformed tokens or out-of-range values. Include no explanation outside the code."
        )
        example_id = f"{track}-beginner-normalize-list-{fence.lower()}-code"
        require(example_id not in ids, f"duplicate training id: {example_id}")
        ids.add(example_id)
        source = (ROOT / "curriculum/examples/polyglot" / source_rel).read_text(encoding="utf-8").rstrip()
        train.append({
            "id": example_id,
            "track": track,
            "level": "beginner",
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": f"```{fence}\n{source}\n```"},
            ],
        })
    require(len(train) == track_count * 3 + len(EXAMPLES), "v2 should add checked coding answers to every v1 training row")
    valid = lines(BASE / "valid.jsonl")
    evaluation = lines(BASE / "eval.jsonl")
    train_prompts = {row["messages"][0]["content"] for row in train}
    valid_prompts = {row["messages"][0]["content"] for row in valid}
    eval_prompts = {row["prompt"] for row in evaluation}
    require(not train_prompts & valid_prompts, "train and validation prompts overlap")
    require(not train_prompts & eval_prompts, "training prompts overlap held-out evaluation")
    require(len(valid) == track_count and len(evaluation) == track_count, "held-out v1 split sizes changed unexpectedly")
    code_eval = []
    for track, display, language in CODE_EVAL:
        code_eval.append({
            "id": f"code-{track}-{language}-heldout",
            "track": track,
            "level": "beginner",
            "language": language,
            "must_include": ["```"],
            "prompt": (
                f"In {display}, write a standalone stdin program that accepts one comma-delimited line of signed 32-bit integers, "
                "outputs a JSON array in ascending order with duplicates removed, and outputs [] when the line is blank. "
                "Reject a malformed token or out-of-range integer by exiting nonzero and writing nothing to stdout. "
                "Return only one fenced source code block; do not explain it."
            ),
        })
    require(not {row["prompt"] for row in code_eval} & train_prompts, "code evaluation prompt overlaps training")
    return {
        "train.jsonl": encode(train),
        "valid.jsonl": encode(valid),
        "eval.jsonl": encode(evaluation),
        "code-eval.jsonl": encode(code_eval),
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def encode(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    if args.check:
        changed = [name for name, data in outputs.items() if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if changed:
            raise SystemExit("Generated v2 dataset is stale: " + ", ".join(changed))
        print("Committed code-focused dataset matches its source.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    print(f"Wrote {len(outputs['train.jsonl'].splitlines())} training, {len(outputs['valid.jsonl'].splitlines())} validation, {len(outputs['eval.jsonl'].splitlines())} held-out rubric, and nine held-out code cases.")


if __name__ == "__main__":
    main()
