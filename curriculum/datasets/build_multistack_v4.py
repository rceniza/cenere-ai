#!/usr/bin/env python3
"""Build fact-correction and simpler executable code tasks from v3."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent / "cenere-multistack-v3"
BASE_CODE = Path(__file__).resolve().parent / "cenere-multistack-v2" / "code-eval.jsonl"
OUT = Path(__file__).resolve().parent / "cenere-multistack-v4"
EXAMPLES = [
    ("c", "C", "c/sum_int32.c", "c"),
    ("cpp", "C++", "cpp/sum_int32.cpp", "cpp"),
    ("php", "PHP", "php/sum_int32.php", "php"),
    ("javascript", "JavaScript", "node/sum_int32.js", "javascript"),
    ("typescript", "TypeScript", "typescript/sum_int32.ts", "typescript"),
    ("nodejs", "Node.js", "node/sum_int32.js", "javascript"),
    ("python", "Python", "python/sum_int32.py", "python"),
    ("rust", "Rust", "rust/sum_int32.rs", "rust"),
    ("go", "Go", "go/sum_int32.go", "go"),
    ("java", "Java", "java/SumInt32.java", "java"),
    ("csharp", "C#", "csharp/sum_int32.cs", "csharp"),
]

CORRECTIONS = [
    ("legacy-systems", "Fortran", "Are Fortran arrays zero-based? Explain how lower bounds are determined.",
     "No. Fortran arrays are not inherently zero-based. When a declaration omits the lower bound it normally defaults to 1, but an array can declare another lower bound such as `a(0:n)` or `a(-2:n)`. An assumed-shape dummy like `x(:)` has lower bound 1 unless the dummy declaration specifies one; use `lbound` and `ubound` when the actual bounds matter."),
    ("database-engines", "SQLite WAL", "How many SQLite writers can write concurrently in WAL mode, and what can overlap?",
     "WAL allows readers and a writer to make progress concurrently, but SQLite still permits only one writer at a time because a database has one WAL file. Keep write transactions short, handle busy results, and checkpoint the WAL as appropriate. WAL uses shared memory and is intended for processes on the same machine, not a network filesystem."),
    ("frontend-frameworks", "Next.js", "In the App Router, what marks a client component boundary? Is `useClient` a hook?",
     "The `'use client'` directive at the top of a module declares a client entry point; it is not a `useClient` hook. Use a client boundary for state, event handlers, effects, or browser APIs, and keep it as deep in the tree as practical. Server Components remain the default and can pass serializable props to Client Components."),
    ("mobile-desktop", "Tauri", "How should a Tauri v2 webview get restricted filesystem access?",
     "Use the official filesystem plugin API such as `@tauri-apps/plugin-fs`, or perform the operation in a narrow Rust command. Grant only the required plugin commands and paths through a window capability and filesystem scope. Do not assume a global `window.tract` API or enable unrestricted filesystem access."),
    ("backend-frameworks", "ASP.NET Core", "What is the lifetime problem when a singleton depends on a scoped service?",
     "A scoped service belongs to a request or explicitly created scope. Injecting it into a singleton captures scoped state beyond its intended lifetime and can cause a captive dependency; development scope validation detects this. Create a scope for background work that needs scoped services. A transient service has different lifetime semantics and is not the same scope violation."),
    ("frontend-frameworks", "React", "Show the lifecycle pattern for preventing an old fetch response from updating a screen after navigation.",
     "Create an `AbortController` for the request, pass its signal to `fetch`, and abort it in the effect cleanup when the route or query changes or the component unmounts. Handle abort separately from ordinary errors. If a client cannot cancel the operation, use a request identity or active flag to ignore stale results."),
    ("mobile-desktop", "Kotlin", "What should happen to screen-owned coroutine work when its lifecycle ends?",
     "Launch work in a lifecycle-owned structured scope so cancellation propagates to child coroutines when the screen is destroyed or its owner stops the work. Do not detach screen tasks into a global scope. Put blocking work on an appropriate dispatcher and test cancellation during an in-flight operation."),
    ("legacy-systems", "COBOL", "What does a COBOL PIC clause tell you during record migration?",
     "A `PIC` clause describes a field's representation and editing, including its size and numeric shape; related `USAGE`, sign, and decimal scaling affect the stored value. Preserve field order and record length as well as encoding and packed-decimal details when the record is a file or service contract. Verify with byte-level fixtures from real records."),
    ("backend-frameworks", "Spring", "Does Spring `@Transactional` make a database write and remote HTTP call atomic together?",
     "No. A local Spring database transaction does not automatically include a remote HTTP service. A database commit can succeed while the remote call fails, or vice versa. For reliable cross-service work, consider a transactional outbox, idempotent message handling, and a saga with explicit compensation; do not claim XA or a local transaction makes arbitrary HTTP calls atomic."),
    ("build-toolchains", "Code generation", "When asked for standalone C using only the standard library, what checks should a coding agent make before returning the answer?",
     "Return C source rather than shell or another language, use only standard-library headers unless the prompt permits dependencies, and ensure the program compiles with the requested compiler mode. Check input boundaries, exact stdout and exit status, and malformed input. Do not invent an installed JSON library; either implement the requested format with permitted facilities or explain the constraint."),
]

VALID = [
    ("legacy-systems", "intermediate", "In a Fortran assumed-shape dummy array, how can a procedure learn its actual bounds?", "Use `lbound` and `ubound`; do not assume zero-based indexing."),
    ("database-engines", "intermediate", "Can two SQLite write transactions append to the WAL at the same time?", "No. WAL permits one writer at a time, while readers can overlap with a writer."),
    ("frontend-frameworks", "advanced", "How do you mark a Next.js App Router entry point that needs browser APIs?", "Add the `'use client'` directive at the top of the module; it is a directive, not a hook."),
    ("mobile-desktop", "advanced", "Where do Tauri v2 filesystem plugin permissions and path limits come from?", "The app window's capability declares plugin permissions and the plugin scope restricts accessible paths."),
    ("backend-frameworks", "intermediate", "Why should an ASP.NET Core singleton not retain a request-scoped DbContext?", "The scoped DbContext must not outlive its request scope; create a scope for background work."),
    ("frontend-frameworks", "intermediate", "What two actions prevent stale React fetch results after an effect reruns?", "Abort the previous request with AbortController during cleanup, or ignore its result using request identity."),
    ("mobile-desktop", "intermediate", "What propagates cancellation through Kotlin structured concurrency?", "The parent Job and lifecycle-owned coroutine scope cancel their child coroutines."),
    ("legacy-systems", "intermediate", "Which COBOL record details affect numeric decoding?", "PIC, USAGE, signedness, decimal scale, field order, and encoding."),
    ("backend-frameworks", "advanced", "What pattern helps reliably publish an event after a Spring database transaction commits?", "A transactional outbox plus idempotent consumers; distributed work may also need a saga."),
    ("build-toolchains", "beginner", "How do you validate that a generated standalone C answer meets its prompt?", "Compile using the requested standard library/compiler mode and run valid, boundary, and malformed-input cases while checking stdout and exit status."),
]

EVAL = [
    ("legacy-systems", "advanced", "fortran-bounds", "Fortran lower bounds", "A routine receives an array section with a non-one lower bound. Is Fortran zero-based, and how should the routine inspect bounds?", [["not zero-based", "not inherently zero", "default lower bound is 1"], ["lbound", "lower bound"]], ["zero-based"]),
    ("database-engines", "intermediate", "sqlite-wal", "SQLite WAL writers", "Does SQLite WAL permit multiple concurrent writers? Explain which readers and writers can overlap.", [["one writer", "single writer"], ["readers", "reader and writer", "readers do not block writers"]], ["unlimited writers", "no concurrency limit"]),
    ("frontend-frameworks", "advanced", "next-boundary", "Next.js directive", "Name the App Router directive for a client component and one case that needs it.", [["use client"], ["browser api", "event handler", "state", "interactivity"]], ["useclient hook"]),
    ("mobile-desktop", "advanced", "tauri-scope", "Tauri filesystem", "Can a Tauri v2 frontend call `window.tract` for unrestricted file access? What should it use instead?", [["plugin-fs", "plugin-fs", "@tauri-apps/plugin-fs", "rust command"], ["capability", "permission"], ["scope", "restrict"]], ["window.tract", "unrestricted access"]),
    ("backend-frameworks", "intermediate", "aspnet-lifetime", "ASP.NET scoped lifetime", "Which dependency lifetime is invalid to capture in a singleton: scoped or transient? Why?", [["scoped"], ["scope", "lifetime"]], ["transient is the scope violation"]),
    ("frontend-frameworks", "intermediate", "react-abort", "React stale requests", "What browser API should a React effect use to cancel a fetch during cleanup?", [["abortcontroller", "abort controller"], ["cleanup", "abort"]], ["ignore stale results"]),
    ("mobile-desktop", "intermediate", "kotlin-cancel", "Kotlin lifecycle", "What happens to a screen-owned child coroutine when its structured parent is cancelled?", [["cancel"], ["child", "lifecycle", "parent job"]], ["global scope"]),
    ("legacy-systems", "intermediate", "cobol-pic", "COBOL PIC", "What does PIC specify and which numeric storage details must migration preserve?", [["picture", "pic"], ["scale", "sign", "usage"]], ["field names only"]),
    ("backend-frameworks", "advanced", "spring-outbox", "Spring remote transactions", "Does a local Spring transaction include a remote HTTP service, and what pattern can make publishing reliable?", [["does not", "not automatically", "no"], ["outbox", "saga"]], ["http is atomic", "xa guarantees arbitrary http"]),
    ("build-toolchains", "intermediate", "code-language", "Code language fidelity", "A request asks for standalone C with no third-party dependencies. Is a Bash script using jq a valid answer? What should be checked?", [["no", "not valid"], ["compile", "standard library"], ["exit status", "stdout"]], ["bash is valid", "jq is required"]),
]


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def encode(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def render() -> dict[str, bytes]:
    train = read_rows(BASE / "train.jsonl")
    for index, (track, technology, prompt, answer) in enumerate(CORRECTIONS, 1):
        train.append({"id": f"correction-{index}-{technology.lower().replace(' ', '-')}", "track": track,
                      "level": "intermediate", "messages": [{"role": "user", "content": prompt},
                                                               {"role": "assistant", "content": answer}]})
    for track, language, source_rel, fence in EXAMPLES:
        prompt = (f"Write a complete standalone {language} command-line program using only its standard library. Read exactly two "
                 "signed 32-bit integers separated by whitespace from stdin, then print their sum followed by a newline. Reject missing or extra tokens, malformed or out-of-range operands, and a sum outside signed 32-bit range by exiting non-zero with no stdout. Return only one fenced source block.")
        code = (ROOT / "curriculum/examples/polyglot" / source_rel).read_text(encoding="utf-8").rstrip()
        train.append({"id": f"sum-int32-{track}-{language.lower().replace('+', 'p').replace('.', '')}",
                      "track": "go-java" if track == "java" else track, "level": "beginner",
                      "messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": f"```{fence}\n{code}\n```"}]})
    valid = read_rows(BASE / "valid.jsonl")
    for index, (track, level, prompt, answer) in enumerate(VALID, 1):
        valid.append({"id": f"correction-valid-{index}", "track": track, "level": level,
                      "messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]})
    evaluation = read_rows(BASE / "eval.jsonl")
    for track, level, name, _topic, prompt, groups, forbidden in EVAL:
        evaluation.append({"id": f"correction-{name}-heldout", "track": track, "level": level,
                           "prompt": prompt, "must_include_any": groups, "must_not_include": forbidden})
    code_eval = read_rows(BASE_CODE)
    for track, language, _source, fence in EXAMPLES:
        code_eval.append({"id": f"sum-int32-{track}-heldout", "track": "go-java" if track == "java" else track,
                          "level": "beginner", "language": track,
                          "exercise": "sum-int32", "must_include": [f"```{fence}"],
                          "prompt": (f"Write a standalone {language} program using only its standard library. Read exactly two signed 32-bit integers separated by whitespace from stdin, print their sum and a newline, and reject malformed/extra tokens, operand overflow, or sum overflow with a non-zero exit and no stdout. Return only one fenced {fence} code block.")})
    ids = [row["id"] for name in ("train", "valid", "eval") for row in {"train": train, "valid": valid, "eval": evaluation}[name]]
    require(len(ids) == len(set(ids)), "duplicate dataset IDs")
    prompts_train = {row["messages"][0]["content"] for row in train}
    prompts_valid = {row["messages"][0]["content"] for row in valid}
    prompts_eval = {row["prompt"] for row in evaluation}
    require(not prompts_train & prompts_valid, "train and validation prompts overlap")
    require(not prompts_train & prompts_eval, "train and evaluation prompts overlap")
    require(not prompts_valid & prompts_eval, "validation and evaluation prompts overlap")
    require(len({row["id"] for row in code_eval}) == len(code_eval), "duplicate code evaluation IDs")
    require({row["exercise"] for row in code_eval if "exercise" in row} == {"sum-int32"}, "sum code cases missing exercise labels")
    return {"train.jsonl": encode(train), "valid.jsonl": encode(valid), "eval.jsonl": encode(evaluation), "code-eval.jsonl": encode(code_eval)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    if args.check:
        changed = [name for name, data in outputs.items() if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if changed:
            raise SystemExit("Generated v4 dataset is stale: " + ", ".join(changed))
        print("Committed correction dataset matches its curated source.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    print(f"Wrote {len(outputs['train.jsonl'].splitlines())} training, {len(outputs['valid.jsonl'].splitlines())} validation, {len(outputs['eval.jsonl'].splitlines())} rubric, and {len(outputs['code-eval.jsonl'].splitlines())} executable code cases.")


if __name__ == "__main__":
    main()
