#!/usr/bin/env python3
"""Execute held-out code answers against the shared polyglot behavior cases."""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

CASES = [
    ("3, 1,3,-2, 1\n", 0, "[-2,1,3]\n"),
    ("\n", 0, "[]\n"),
    ("-2147483648,2147483647\n", 0, "[-2147483648,2147483647]\n"),
    ("1,,2\n", 2, ""),
    ("1,\n", 2, ""),
    ("1,not-a-number\n", 2, ""),
    ("2147483648\n", 2, ""),
]
SUM_CASES = [
    ("10 -3\n", 0, "7\n"),
    ("-2147483648 0\n", 0, "-2147483648\n"),
    ("2147483647 1\n", 2, ""),
    ("2147483648 0\n", 2, ""),
    ("1 x\n", 2, ""),
    ("1 2 3\n", 2, ""),
    ("\n", 2, ""),
]
LANGUAGES = {
    "c": ("cc", "main.c", ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror"]),
    "cpp": ("c++", "main.cpp", ["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror"]),
    "php": ("php", "main.php", None),
    "javascript": ("node", "main.js", None),
    "typescript": ("node", "main.ts", ["node", "--experimental-strip-types"]),
    "nodejs": ("node", "main.js", None),
    "python": ("python3", "main.py", None),
    "rust": ("rustc", "main.rs", ["rustc", "--edition=2021"]),
    "go": ("go", "main.go", ["go", "build"]),
    "java": ("javac", "Main.java", ["javac"]),
}


def fenced_code(answer: str, language: str) -> Optional[str]:
    aliases = {
        "c": {"c"},
        "cpp": {"cpp", "c++"},
        "php": {"php"},
        "javascript": {"javascript", "js", "jsx", "typescript", "ts"},
        "typescript": {"typescript", "ts"},
        "nodejs": {"javascript", "js", "node", "nodejs"},
        "python": {"python", "py"},
        "rust": {"rust", "rs"},
        "go": {"go"},
        "java": {"java"},
    }
    for match in re.finditer(r"```([^\s`]*)[^\n]*\n(.*?)```", answer, re.DOTALL):
        if match.group(1).lower() in aliases.get(language, set()):
            return match.group(2).strip()
    return None


def run_case(command: list[str], input_text: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, input=input_text, text=True, capture_output=True, timeout=30, check=False)


def check(case: dict, answer: str) -> list[str]:
    language = case["language"]
    if language not in LANGUAGES:
        return [f"unsupported language {language}"]
    command_name, filename, compiler = LANGUAGES[language]
    if shutil.which(command_name) is None:
        return [f"toolchain unavailable: {command_name}"]
    if language == "java":
        java = shutil.which("java")
        if java is None:
            return ["toolchain unavailable: java runtime"]
        try:
            if subprocess.run([java, "-version"], capture_output=True, timeout=5, check=False).returncode:
                return ["toolchain unavailable: java runtime"]
        except (OSError, subprocess.TimeoutExpired):
            return ["toolchain unavailable: java runtime"]
    source = fenced_code(answer, language)
    if not source:
        return ["missing fenced source code"]

    failures = []
    with tempfile.TemporaryDirectory(prefix=f"cenere-code-{language}-") as temp_name:
        temp = Path(temp_name)
        exercise = case.get("exercise", "normalize-list")
        if exercise == "sum-int32":
            sum_files = {"c": "sum_int32.c", "cpp": "sum_int32.cpp", "php": "sum_int32.php", "javascript": "sum_int32.js", "typescript": "sum_int32.ts", "nodejs": "sum_int32.js", "python": "sum_int32.py", "rust": "sum_int32.rs", "go": "sum_int32.go", "java": "SumInt32.java"}
            filename = sum_files[language]
        elif exercise != "normalize-list":
            return [f"unsupported exercise {exercise}"]
        source_path = temp / filename
        source_path.write_text(source + "\n", encoding="utf-8")
        if language in {"c", "cpp", "rust", "go", "java"}:
            binary = temp / "program"
            if language in {"c", "cpp", "rust"}:
                build = [*compiler, str(source_path), "-o", str(binary)]
            elif language == "go":
                build = [*compiler, "-o", str(binary), str(source_path)]
            else:
                build = [*compiler, "-d", str(temp), str(source_path)]
            result = subprocess.run(build, text=True, capture_output=True, timeout=60, check=False)
            if result.returncode:
                return ["compile failed: " + result.stderr[-1200:]]
            java_class = "SumInt32" if exercise == "sum-int32" else "Main"
            command = ["java", "-cp", str(temp), java_class] if language == "java" else [str(binary)]
        elif language == "php":
            command = ["php", str(source_path)]
        elif language in {"javascript", "nodejs"}:
            command = ["node", str(source_path)]
        elif language == "typescript":
            command = [*compiler, str(source_path)]
        else:
            command = ["python3", str(source_path)]

        test_cases = SUM_CASES if exercise == "sum-int32" else CASES
        for index, (stdin, expected_code, expected_stdout) in enumerate(test_cases, 1):
            try:
                result = run_case(command, stdin)
            except subprocess.TimeoutExpired:
                failures.append(f"case {index}: timed out")
                continue
            if result.returncode != expected_code or result.stdout != expected_stdout:
                failures.append(f"case {index}: exit={result.returncode}, stdout={result.stdout!r}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True, help="JSONL output from training/evaluate.py")
    args = parser.parse_args()
    predictions = {row["id"]: row["answer"] for row in map(json.loads, args.predictions.read_text(encoding="utf-8").splitlines()) if row.get("answer")}
    total = passed = 0
    for raw in args.cases.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        case = json.loads(raw)
        answer = predictions.get(case["id"], "")
        failures = check(case, answer)
        total += 1
        passed += not failures
        print(f"{case['id']}: {'PASS' if not failures else 'FAIL'}" + (f"; {failures}" if failures else ""), flush=True)
    print(f"Executable score: {passed}/{total}")
    return 0 if total and passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
