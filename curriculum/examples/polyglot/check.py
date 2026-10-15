#!/usr/bin/env python3
"""Compile/run the shared polyglot exercise where toolchains are available."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = [
    ("3, 1,3,-2, 1", 0, "[-2,1,3]\n"),
    ("", 0, "[]\n"),
    ("-2147483648,2147483647", 0, "[-2147483648,2147483647]\n"),
    ("1,,2", 2, ""),
    ("1,", 2, ""),
    ("1,not-a-number", 2, ""),
    ("2147483648", 2, ""),
]


def available(command: str) -> bool:
    if shutil.which(command) is None:
        return False
    if command == "java":
        try:
            return subprocess.run([command, "-version"], capture_output=True, timeout=5, check=False).returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            return False
    return True


def run(command: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, input=input_text, text=True, capture_output=True, timeout=30, check=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require", help="comma-separated languages that must be available")
    args = parser.parse_args()
    required = set(args.require.split(",")) if args.require else set()
    known = {"rust", "c", "cpp", "python", "node", "php", "go", "java"}
    if required - known:
        parser.error(f"unknown language(s): {', '.join(sorted(required - known))}")

    with tempfile.TemporaryDirectory(prefix="cenere-polyglot-") as temp_name:
        temp = Path(temp_name)
        plans: dict[str, tuple[list[str], list[str]]] = {
            "rust": (["rustc"], ["rustc", "--edition=2021", str(ROOT / "rust/main.rs"), "-o", str(temp / "rust")]),
            "c": (["cc"], ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", str(ROOT / "c/main.c"), "-o", str(temp / "c")]),
            "cpp": (["c++"], ["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", str(ROOT / "cpp/main.cpp"), "-o", str(temp / "cpp")]),
            "python": (["python3"], ["python3", str(ROOT / "python/main.py")]),
            "node": (["node"], ["node", str(ROOT / "node/main.js")]),
            "php": (["php"], ["php", str(ROOT / "php/main.php")]),
            "go": (["go"], ["go", "build", "-o", str(temp / "go"), str(ROOT / "go/main.go")]),
            "java": (["javac", "java"], ["javac", "-d", str(temp), str(ROOT / "java/Main.java")]),
        }
        runnable: dict[str, list[str]] = {}
        failures = 0
        for language, (tools, build) in plans.items():
            missing_tools = [tool for tool in tools if not available(tool)]
            if missing_tools:
                status = f"FAIL (missing {', '.join(missing_tools)})" if language in required else f"SKIP (missing {', '.join(missing_tools)})"
                print(f"{language}: {status}")
                failures += language in required
                continue
            if language in {"rust", "c", "cpp", "go"}:
                result = run(build)
                if result.returncode:
                    print(f"{language}: BUILD FAIL\n{result.stderr}")
                    failures += 1
                    continue
                runnable[language] = [str(temp / language)]
            elif language == "java":
                result = run(build)
                if result.returncode:
                    print(f"java: BUILD FAIL\n{result.stderr}")
                    failures += 1
                    continue
                runnable[language] = ["java", "-cp", str(temp), "Main"]
            else:
                runnable[language] = build

        for language, command in runnable.items():
            for index, (input_text, expected_status, expected_stdout) in enumerate(CASES, 1):
                result = run(command, input_text=input_text + "\n")
                if result.returncode != expected_status or result.stdout != expected_stdout:
                    print(f"{language} case {index}: FAIL (exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr.strip()!r})")
                    failures += 1
                else:
                    print(f"{language} case {index}: PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
