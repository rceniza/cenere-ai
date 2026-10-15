#!/usr/bin/env python3
"""Extend verified patch-repair training with Go and C# examples."""

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "cenere-problem-solving-v5"
PREVIOUS = ROOT / "cenere-problem-solving-v4"
SPEC = importlib.util.spec_from_file_location("problem_solving_v4", ROOT / "build_problem_solving_v4.py")
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)

PATCHES = [
    {
        "id": "repair-go-first-nonempty-trimmed",
        "track": "go-java",
        "level": "intermediate",
        "fixture": "patch-repair-v1/fixtures/train-go-first-nonempty",
        "file": "strings.go",
        "context_files": ["go.mod", "strings.go"],
        "language": "go",
        "task": "Fix `firstNonEmpty` to return the first non-empty string after trimming surrounding whitespace, or the empty string when none qualify. Preserve the signature. Return only a fenced unified git diff.",
        "checks": [["go", "test", "."]],
        "fixed": '''package patchtrain

import "strings"

func firstNonEmpty(values []string) string {
	for _, value := range values {
		if trimmed := strings.TrimSpace(value); trimmed != "" {
			return trimmed
		}
	}
	return ""
}
''',
    },
    {
        "id": "repair-csharp-tags-normalized",
        "track": "csharp",
        "level": "intermediate",
        "fixture": "patch-repair-v1/fixtures/train-csharp-tags",
        "file": "TagParser.cs",
        "context_files": ["Check.csproj", "TagParser.cs"],
        "language": "csharp",
        "task": "Fix `TagParser.Parse` to split comma-separated tags, trim them, discard blanks, and deduplicate case-insensitively while preserving the first spelling and order. Preserve the public signature and standard-library-only implementation. Return only a fenced unified git diff.",
        "checks": [["dotnet", "run", "--project", "Check.csproj", "--configuration", "Release", "--verbosity", "quiet"]],
        "fixed": '''using System;
using System.Collections.Generic;

public static class TagParser
{
    public static List<string> Parse(string input)
    {
        var result = new List<string>();
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var part in input.Split(','))
        {
            var tag = part.Trim();
            if (tag.Length > 0 && seen.Add(tag))
            {
                result.Add(tag);
            }
        }
        return result;
    }
}
''',
    },
]


def render() -> dict[str, bytes]:
    rendered = {name: (PREVIOUS / name).read_bytes() for name in ("valid.jsonl", "eval.jsonl")}
    train = [json.loads(line) for line in (PREVIOUS / "train.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    for item in PATCHES:
        source = BUILDER.FIXTURES / item["fixture"] / "files" / item["file"]
        original = source.read_text(encoding="utf-8")
        prompt = item["task"] + f"\n\nSource file `{item['file']}`:\n```{item['language']}\n{original}```"
        patch = BUILDER.make_diff(item["file"], original, item["fixed"])
        train.append({"id": item["id"], "track": item["track"], "level": item["level"],
                      "messages": [{"role": "user", "content": prompt},
                                   {"role": "assistant", "content": f"```diff\n{patch}```"}]})
    ids = [row["id"] for row in train]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate problem-solving v5 training IDs")
    rendered["train.jsonl"] = BUILDER.encode(train)
    return rendered


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    if args.check:
        stale = [name for name, data in outputs.items() if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if stale:
            raise SystemExit("Problem-solving v5 dataset is stale: " + ", ".join(stale))
        print("Problem-solving v5 dataset matches its curated source.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    print(f"Wrote {len(outputs['train.jsonl'].splitlines())} training rows and preserved held-out validation/evaluation rows.")


if __name__ == "__main__":
    main()
