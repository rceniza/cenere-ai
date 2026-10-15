#!/usr/bin/env python3
"""Add a small reviewed problem-solving curriculum on top of multistack v4."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "cenere-multistack-v4"
OUT = ROOT / "cenere-problem-solving-v1"

TRAIN = [
    ("Debugging", "A test fails only in CI. How should you investigate?", "First reproduce the failure and capture the exact command, environment, and error. Compare CI and local versions, configuration, locale, time zone, filesystem assumptions, and parallelism. Reduce the failure to the smallest case, form one hypothesis at a time, and add a regression test before changing code. Rerun the failing test and the relevant suite; report what was verified and what remains uncertain."),
    ("Test design", "How do you turn a vague feature request into an implementation plan?", "Restate the expected user-visible behavior and identify missing decisions. Ask about ambiguities that change data, security, or API behavior; otherwise state a small reversible assumption. List constraints and edge cases, choose the smallest design that satisfies them, and define observable acceptance tests before implementation. Implement one slice, run the tests, inspect the diff, and update the plan from evidence."),
    ("Test diagnosis", "A new unit test fails after a refactor. What do you do first?", "Read the assertion and failure output, then compare the intended contract with the changed behavior. Do not weaken the assertion just to make it pass. Reproduce the failure in isolation, inspect the smallest relevant diff, and decide whether the implementation or test assumption is wrong. Fix the cause, add a regression case if needed, and run both the focused test and the full relevant suite."),
    ("Performance", "An endpoint is slow, but there is no profile yet. Should you add a cache?", "Measure first. Record latency and throughput for representative requests, then profile CPU, database queries, network waits, and allocation. Identify the dominant cost and establish a baseline. A cache is appropriate only if repeated reads dominate and a correct invalidation or freshness rule exists. Change one bottleneck at a time and compare measurements while checking correctness under concurrent updates."),
    ("Database race", "Two workers occasionally create duplicate accounts for the same email. What is a robust fix?", "Treat this as a concurrency invariant. Normalize the email consistently and enforce uniqueness with a database constraint, because an application-level check followed by insert has a race. Handle the unique-violation result as an expected conflict and test two concurrent creates. Review existing duplicate data and migration behavior before adding the constraint."),
    ("Research", "A framework API may have changed between major versions. How should a coding agent answer?", "Identify the exact framework and version from project files or ask if it is missing. Check the version-matched official documentation or release notes, and distinguish verified behavior from inference. Prefer a small example that matches the installed version. If the source cannot be confirmed, say so and avoid inventing a method name; provide a way to verify it locally."),
    ("Tool use", "When should a coding agent run a shell command or edit a file?", "Choose a tool only when it advances a stated step: inspect relevant files, run a focused test, or apply a narrow patch. Explain consequential commands before asking for permission when the configured policy requires it. Avoid destructive or broad commands without explicit authorization. After an edit, inspect the diff and run the smallest relevant verification, then report the actual result."),
    ("Planning", "A task spans an API, database migration, and UI. How should you reduce delivery risk?", "Trace the data and contract across the layers, then define one end-to-end acceptance case. Identify compatibility, migration, rollback, and authorization constraints first. Implement a vertical slice behind a compatible contract, test the migration against representative data, and verify the UI and API together. Keep changes reviewable and state deployment ordering if old and new versions overlap."),
    ("Uncertainty", "What should you do when evidence does not support a confident answer?", "State what is known, what is uncertain, and which assumption would change the recommendation. Check local source, tests, configuration, or authoritative versioned documentation when available. Ask one targeted question if the uncertainty blocks a safe or useful choice. Do not fill the gap with a confident-sounding guess; offer a reversible next step to obtain evidence."),
    ("Code review", "How should an agent review its own generated patch?", "Compare the patch with the requested behavior and inspect every changed file. Look for boundary errors, security and data handling, compatibility, missing tests, accidental unrelated edits, and generated files. Run focused tests and static checks relevant to the change, then inspect the final diff again. Report commands and outcomes accurately; a passing test suite does not prove untested behavior."),
    ("Algorithm choice", "How do you choose between a simple scan and a more complex index?", "Start from input size, update frequency, latency target, and memory budget. A linear scan may be the clearest choice for small or rarely queried data. Estimate the expected query cost and index maintenance cost, then benchmark representative workloads if the choice matters. Add the index only when measured use justifies its complexity and verify boundary cases and update consistency."),
    ("Incident response", "A deployment health check fails after a release. What should the agent do?", "Use the service's documented rollback or stop procedure if users are affected; do not improvise destructive production commands. Capture health-check output, release identifier, logs, and recent configuration changes. Compare against the last known good version, isolate the failing component, and verify recovery with the same health check. Preserve evidence and propose a tested fix before redeploying."),
]

VALID = [
    ("A database check-then-insert passes unit tests but duplicates appear under load. What should change?", "Enforce the invariant in the database with a unique constraint, handle the conflict, and test concurrent inserts."),
    ("An optimization makes a benchmark faster but changes output on empty input. Is it ready?", "No. Preserve the behavior contract, add an empty-input regression test, fix it, and rerun correctness and performance checks."),
    ("A library example uses an API absent from the installed version. What is the next step?", "Check the installed version and its official version-matched documentation; do not guess a replacement API."),
    ("A broad test suite takes an hour and one focused test is failing. What do you run first?", "Reproduce with the focused test, diagnose from the failure, then run the relevant suite after the fix."),
    ("A task has an unclear default that affects authorization. Should the agent silently assume?", "No. Ask for clarification or choose a fail-closed behavior and state the assumption."),
    ("A patch passes tests but changes unrelated formatting across many files. What should review do?", "Remove unrelated changes, inspect the focused diff, and rerun relevant tests."),
]

EVAL = [
    ("ci-flake", "A test fails once in 40 CI runs and never on a developer laptop. What evidence do you collect before changing code?", [["reproduce", "failure output", "failing command"], ["environment", "parallel", "timing", "versions"], ["hypothesis", "isolate", "smallest"]], ["add a retry", "ignore the failure"]),
    ("cache-decision", "A dashboard feels slow. What should you measure before introducing a cache, and what correctness rule must you define?", [["profile", "measure", "baseline", "latency"], ["dominant", "bottleneck", "query"], ["invalidation", "freshness", "stale"]], ["always cache", "cache everything"]),
    ("unique-race", "An application checks that a username is unused, then inserts it; duplicates appear under concurrent requests. What enforces correctness?", [["unique constraint", "unique index", "database constraint"], ["race", "concurrent"], ["conflict", "unique violation"]], ["check then insert is sufficient"]),
    ("api-version", "A code sample calls a method that cannot be found in the installed framework package. What should the agent verify?", [["version", "installed package"], ["official documentation", "release notes"], ["avoid guessing", "do not invent"]], ["use the latest api without checking"]),
    ("production-health", "A production health check fails immediately after deployment. What is a safe initial response?", [["rollback", "documented rollback", "stop procedure"], ["capture", "logs", "release identifier"], ["verify recovery", "health check"]], ["drop database", "rerun deploy immediately"]),
    ("patch-review", "A change passes its new unit test. What else should a coding agent inspect before calling it done?", [["diff", "changed files"], ["edge", "security", "compatibility"], ["relevant suite", "focused test"]], ["tests prove everything"]),
    ("ambiguous-auth", "A feature request leaves unclear whether private records are visible to project members or only owners. What should the agent do?", [["ask", "clarify", "question"], ["authorization", "privacy", "access"], ["fail closed", "assumption"]], ["assume all members"]),
    ("migration", "A service and database migration must deploy while old and new service versions overlap. Which compatibility concern belongs in the plan?", [["backward compatible", "compatibility"], ["old and new", "overlap", "rollout"], ["rollback", "migration"]], ["replace column immediately"]),
    ("algorithm", "A 500-row table is read twice a day but updated continuously. Should the agent add a complex in-memory index without measurement?", [["measure", "benchmark", "workload"], ["update cost", "maintenance", "memory"], ["simple scan", "linear scan"]], ["index is always faster"]),
    ("test-fix", "A refactor breaks a test that encoded a documented contract. What must not be the first fix?", [["do not weaken", "do not delete", "preserve the assertion"], ["reproduce", "inspect"], ["regression test", "root cause"]], ["delete the failing test"]),
]


def read(name: str) -> list[dict]:
    return [json.loads(x) for x in (BASE / name).read_text().splitlines() if x.strip()]


def dump(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n").encode()


def render() -> dict[str, bytes]:
    train, valid, evaluation = read("train.jsonl"), read("valid.jsonl"), read("eval.jsonl")
    for i, (topic, prompt, answer) in enumerate(TRAIN, 1):
        train.append({"id": f"problem-solving-{i:02}", "track": "problem-solving", "level": "intermediate",
                      "messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]})
    for i, (prompt, answer) in enumerate(VALID, 1):
        valid.append({"id": f"problem-solving-valid-{i:02}", "track": "problem-solving", "level": "intermediate",
                      "messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]})
    for name, prompt, groups, forbidden in EVAL:
        evaluation.append({"id": f"problem-solving-{name}-heldout", "track": "problem-solving", "level": "intermediate",
                           "prompt": prompt, "must_include_any": groups, "must_not_include": forbidden})
    ids = [row["id"] for rows in (train, valid, evaluation) for row in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate IDs across problem-solving splits")
    train_prompts = {row["messages"][0]["content"] for row in train}
    valid_prompts = {row["messages"][0]["content"] for row in valid}
    eval_prompts = {row["prompt"] for row in evaluation}
    if train_prompts & valid_prompts or train_prompts & eval_prompts or valid_prompts & eval_prompts:
        raise ValueError("problem-solving prompts overlap splits")
    return {"train.jsonl": dump(train), "valid.jsonl": dump(valid), "eval.jsonl": dump(evaluation)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    if args.check:
        stale = [name for name, data in outputs.items() if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if stale:
            raise SystemExit("Dataset is stale: " + ", ".join(stale))
        print("Problem-solving dataset matches its curated source.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    print(f"Wrote {len(outputs['train.jsonl'].splitlines())} training, {len(outputs['valid.jsonl'].splitlines())} validation, and {len(outputs['eval.jsonl'].splitlines())} held-out rubric rows.")


if __name__ == "__main__":
    main()
