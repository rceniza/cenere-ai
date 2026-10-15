#!/usr/bin/env python3
"""Run a small deterministic rubric-based evaluation against a local chat endpoint."""

import argparse
import json
import urllib.request
from pathlib import Path


def score(case: dict, answer: str) -> tuple[list[str], list[str]]:
    lower = answer.lower()
    missing = [term for term in case.get("must_include", []) if term.lower() not in lower]
    for group in case.get("must_include_any", []):
        if not any(term.lower() in lower for term in group):
            missing.append("one of: " + " | ".join(group))
    forbidden = [term for term in case.get("must_not_include", []) if term.lower() in lower]
    return missing, forbidden


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True, help="JSONL cases with prompt/must_include/must_not_include")
    parser.add_argument("--endpoint", default="http://127.0.0.1:8080/v1/chat/completions")
    parser.add_argument("--model", default="default_model")
    parser.add_argument("--max-tokens", type=int, default=320)
    parser.add_argument("--output", type=Path, help="Optional JSONL prediction output")
    args = parser.parse_args()
    if args.max_tokens < 1:
        parser.error("--max-tokens must be positive")

    output = args.output.open("w", encoding="utf-8") if args.output else None
    passed = total = 0
    try:
        for line_number, raw in enumerate(args.cases.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            case = json.loads(raw)
            prompt = case["prompt"]
            if case.get("reference_file"):
                reference = Path(__file__).resolve().parents[1] / case["reference_file"]
                prompt += "\n\nVerified reference implementation:\n```rust\n" + reference.read_text(encoding="utf-8") + "\n```"
            body = json.dumps({
                "model": args.model,
                "messages": [
                    {"role": "system", "content": "Answer the single requested curriculum task directly and concisely. Be technically accurate, state important safety or resource constraints, and do not claim to have run tools or tests."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0,
                "stream": False,
                "max_tokens": args.max_tokens,
            }).encode()
            request = urllib.request.Request(args.endpoint, data=body, headers={"content-type": "application/json"})
            with urllib.request.urlopen(request, timeout=180) as response:
                result = json.load(response)
            answer = result["choices"][0]["message"]["content"]
            missing, forbidden = score(case, answer)
            ok = not missing and not forbidden
            passed += int(ok)
            total += 1
            case_id = case.get("id", f"case-{line_number}")
            track = case.get("track", "unassigned")
            level = case.get("level", "unassigned")
            print(f"{case_id} [{track}/{level}]: {'PASS' if ok else 'FAIL'}; missing={missing}; forbidden={forbidden}", flush=True)
            if output:
                output.write(json.dumps({"case": line_number, "id": case_id, "track": track, "level": level, "passed": ok, "missing": missing, "forbidden": forbidden, "answer": answer}, ensure_ascii=False) + "\n")
                output.flush()
    finally:
        if output:
            output.close()
    print(f"Score: {passed}/{total}")
    return 0 if total > 0 and passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
