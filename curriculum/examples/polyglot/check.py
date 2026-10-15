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
SUM_CASES = [
    ("10 -3", 0, "7\n"),
    ("-2147483648 0", 0, "-2147483648\n"),
    ("2147483647 1", 2, ""),
    ("2147483648 0", 2, ""),
    ("1 x", 2, ""),
    ("1 2 3", 2, ""),
    ("", 2, ""),
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
    # Shared CI runners may need longer to compile C++ and Go from a cold cache.
    return subprocess.run(command, input=input_text, text=True, capture_output=True, timeout=120, check=False)


def prepare_csharp(source: Path, root: Path, name: str) -> tuple[list[str], list[str]]:
    project = root / name
    project.mkdir()
    (project / "Program.cs").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    project_file = project / "CenereExample.csproj"
    project_file.write_text(
        '<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType>'
        '<TargetFramework>net10.0</TargetFramework><ImplicitUsings>disable</ImplicitUsings>'
        '<Nullable>enable</Nullable></PropertyGroup></Project>',
        encoding="utf-8",
    )
    output = project / "out"
    return (
        ["dotnet", "build", str(project_file), "--configuration", "Release", "--output", str(output), "--nologo", "--verbosity", "quiet"],
        ["dotnet", str(output / "CenereExample.dll")],
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--require", help="comma-separated languages that must be available")
    args = parser.parse_args()
    required = set(args.require.split(",")) if args.require else set()
    known = {"rust", "c", "cpp", "python", "node", "typescript", "php", "go", "java", "csharp"}
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
            "typescript": (["node"], ["node", "--experimental-strip-types", str(ROOT / "typescript/main.ts")]),
            "php": (["php"], ["php", str(ROOT / "php/main.php")]),
            "go": (["go"], ["go", "build", "-o", str(temp / "go"), str(ROOT / "go/main.go")]),
            "java": (["javac", "java"], ["javac", "-d", str(temp), str(ROOT / "java/Main.java")]),
            "csharp": (["dotnet"], None),
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
            elif language == "csharp":
                build, command = prepare_csharp(ROOT / "csharp/main.cs", temp, "main")
                result = run(build)
                if result.returncode:
                    print(f"csharp: BUILD FAIL\n{result.stderr}")
                    failures += 1
                    continue
                runnable[language] = command
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

            sum_sources = {
                "rust": "rust/sum_int32.rs", "c": "c/sum_int32.c", "cpp": "cpp/sum_int32.cpp",
                "python": "python/sum_int32.py", "node": "node/sum_int32.js",
                "typescript": "typescript/sum_int32.ts", "php": "php/sum_int32.php",
                "go": "go/sum_int32.go", "java": "java/SumInt32.java",
                "csharp": "csharp/sum_int32.cs",
            }
            source_path = ROOT / sum_sources[language]
            if language == "rust":
                binary = temp / "sum-rust"
                build = ["rustc", "--edition=2021", str(source_path), "-o", str(binary)]
            elif language == "c":
                binary = temp / "sum-c"
                build = ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", str(source_path), "-o", str(binary)]
            elif language == "cpp":
                binary = temp / "sum-cpp"
                build = ["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror", str(source_path), "-o", str(binary)]
            elif language == "go":
                binary = temp / "sum-go"
                build = ["go", "build", "-o", str(binary), str(source_path)]
            elif language == "java":
                build = ["javac", "-d", str(temp), str(source_path)]
                binary = None
            elif language == "csharp":
                build, sum_command = prepare_csharp(source_path, temp, "sum")
                binary = None
            else:
                build = None
                binary = None
            if build:
                result = run(build)
                if result.returncode:
                    print(f"{language} sum build: FAIL\n{result.stderr}")
                    failures += 1
                    continue
            if binary:
                sum_command = [str(binary)]
            elif language == "java":
                sum_command = ["java", "-cp", str(temp), "SumInt32"]
            elif language == "csharp":
                pass
            elif language == "php":
                sum_command = ["php", str(source_path)]
            elif language in {"node", "typescript"}:
                sum_command = ["node", *(["--experimental-strip-types"] if language == "typescript" else []), str(source_path)]
            else:
                sum_command = ["python3", str(source_path)]
            for index, (input_text, expected_status, expected_stdout) in enumerate(SUM_CASES, 1):
                result = run(sum_command, input_text=input_text + "\n")
                if result.returncode != expected_status or result.stdout != expected_stdout:
                    print(f"{language} sum case {index}: FAIL (exit={result.returncode}, stdout={result.stdout!r}, stderr={result.stderr.strip()!r})")
                    failures += 1
                else:
                    print(f"{language} sum case {index}: PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
