#!/usr/bin/env python3
"""Apply model-proposed diffs to isolated bug fixtures and run hidden behavior checks."""

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "curriculum/evaluations"
ALLOWED_COMMANDS = {"python3", "rustc", "node", "npm", "cargo", "php", "go", "javac", "dotnet"}
OUTPUT_LIMIT = 12_000


def extract_diff(answer: str) -> str | None:
    marker = "```diff"
    start = answer.find(marker)
    if start >= 0:
        start = answer.find("\n", start + len(marker))
        if start < 0:
            return None
        end = answer.find("```", start + 1)
        return answer[start + 1:end].strip() + "\n" if end >= 0 else None
    start = answer.find("diff --git ")
    return answer[start:].strip() if start >= 0 else None


def normalize_diff(diff: str) -> str | None:
    if "diff --git " in diff:
        return diff if diff.endswith("\n") else diff + "\n"
    lines = diff.splitlines(keepends=True)
    old_index = next((i for i, line in enumerate(lines) if line.startswith("--- ")), None)
    if old_index is None or old_index + 1 >= len(lines) or not lines[old_index + 1].startswith("+++ "):
        return None
    old = lines[old_index][4:].split("\t", 1)[0].strip().split(" ", 1)[0]
    new = lines[old_index + 1][4:].split("\t", 1)[0].strip().split(" ", 1)[0]
    if old.startswith("a/"):
        old = old[2:]
    if new.startswith("b/"):
        new = new[2:]
    try:
        old_path, new_path = safe_relative_path(old), safe_relative_path(new)
    except ValueError:
        return None
    if old_path != new_path:
        return None
    relative = old_path.as_posix()
    normalized_headers = [f"diff --git a/{relative} b/{relative}\n",
                          f"--- a/{relative}\n", f"+++ b/{relative}\n"]
    normalized = normalized_headers + lines[old_index + 2:]
    result = "".join(normalized)
    return result if result.endswith("\n") else result + "\n"


def safe_relative_path(value: str) -> Path:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or any(part in {".", ".."} for part in path.parts):
        raise ValueError(f"unsafe fixture path: {value}")
    return Path(*path.parts)


def run_command(command: list[str], cwd: Path, timeout: int) -> tuple[bool, str]:
    if not isinstance(command, list) or not command:
        return False, "validation command uses an unsupported executable"
    executable = command[0]
    if executable not in ALLOWED_COMMANDS:
        try:
            relative = safe_relative_path(executable)
        except ValueError:
            return False, "validation command uses an unsupported executable"
        executable_path = (cwd / relative).resolve()
        if not executable_path.is_file() or not executable_path.is_relative_to(cwd.resolve()):
            return False, "validation command uses an unsupported executable"
        command = [str(executable_path), *command[1:]]
    try:
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True,
                                timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s: {command[0]}"
    output = (result.stdout + result.stderr)[-OUTPUT_LIMIT:]
    if result.returncode:
        return False, f"exit={result.returncode}: {output}"
    return True, output


def check(case: dict, answer: str) -> list[str]:
    fixture_name = case.get("fixture")
    try:
        fixture = safe_relative_path(fixture_name)
    except (TypeError, ValueError) as error:
        return [str(error)]
    source = FIXTURE_ROOT / fixture
    if not source.is_dir() or not (source / "files").is_dir():
        return [f"missing fixture: {fixture_name}"]
    extracted = extract_diff(answer)
    diff = normalize_diff(extracted) if extracted else None
    if not diff:
        return ["missing unified diff"]

    with tempfile.TemporaryDirectory(prefix="cenere-patch-eval-") as temp_name:
        work = Path(temp_name)
        for relative in case.get("context_files", []):
            rel = safe_relative_path(relative)
            source_file = source / "files" / rel
            if not source_file.is_file():
                return [f"missing context file: {relative}"]
            destination = work / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, destination)
        hidden_checks = source / "checks"
        if hidden_checks.is_dir():
            shutil.copytree(hidden_checks, work / "checks")
        initialized = subprocess.run(["git", "init", "--quiet"], cwd=work, capture_output=True, timeout=10)
        if initialized.returncode:
            return ["could not initialize isolated patch workspace"]
        checked = subprocess.run(["git", "apply", "--recount", "--check", "-"], input=diff,
                                 text=True, cwd=work, capture_output=True, timeout=10, check=False)
        if checked.returncode:
            return ["patch rejected: " + (checked.stderr or checked.stdout)[-OUTPUT_LIMIT:]]
        applied = subprocess.run(["git", "apply", "--recount", "-"], input=diff,
                                 text=True, cwd=work, capture_output=True, timeout=10, check=False)
        if applied.returncode:
            return ["patch apply failed: " + applied.stderr[-OUTPUT_LIMIT:]]
        failures = []
        for index, command in enumerate(case.get("checks", []), 1):
            ok, output = run_command(command, work, int(case.get("timeout_seconds", 20)))
            if not ok:
                failures.append(f"check {index}: {output}")
        if not case.get("checks"):
            failures.append("fixture has no hidden behavior checks")
        return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    args = parser.parse_args()
    predictions = {
        row["id"]: row.get("answer", "")
        for row in map(json.loads, args.predictions.read_text(encoding="utf-8").splitlines())
        if row.get("id")
    }
    passed = total = 0
    for line_number, raw in enumerate(args.cases.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        case = json.loads(raw)
        answer = predictions.get(case["id"], "")
        failures = check(case, answer)
        total += 1
        passed += not failures
        print(f"{case['id']}: {'PASS' if not failures else 'FAIL'}" + (f"; {failures}" if failures else ""), flush=True)
    print(f"Patch/action score: {passed}/{total}")
    return 0 if total and passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
