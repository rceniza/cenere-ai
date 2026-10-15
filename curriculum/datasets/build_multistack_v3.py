#!/usr/bin/env python3
"""Build a technology-specific extension for the broad multistack dataset."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = Path(__file__).resolve().parent / "cenere-multistack-v2"
OUT = Path(__file__).resolve().parent / "cenere-multistack-v3"

# Curated concept explanations target the concrete technologies named in the
# broad catalog. Keep version-sensitive command/API details out of this seed.
TRAIN = [
    ("frontend-frameworks", "intermediate", "AngularJS", "Plan an AngularJS-to-Angular migration around observable boundaries. Start by inventorying routes, directives, services, and tests, then migrate one vertical feature at a time. Keep temporary compatibility bridges isolated, add behavior tests before replacing a component, and remove each bridge when its dependents are gone. Avoid a rewrite that changes framework and product behavior at the same time."),
    ("frontend-frameworks", "beginner", "Angular", "Use a component to own a focused piece of UI, inputs to receive parent data, and outputs to report user actions. Keep reusable business rules in injectable services when multiple components need them. Test the component's rendered states and the service behavior separately; do not put network or persistence logic into a template."),
    ("frontend-frameworks", "intermediate", "React", "Treat props as read-only inputs and keep state at the lowest common owner that needs to coordinate it. Derive values during render instead of copying props into state. Use effects to synchronize with external systems, with cleanup for subscriptions and requests. Test user-visible behavior and stale asynchronous results."),
    ("frontend-frameworks", "beginner", "Vue", "Use props for parent-to-child data and emits for child-to-parent events. Keep derived values computed from reactive state instead of storing duplicate state. Put reusable stateful behavior in composables and test both the component interaction and edge cases such as empty data."),
    ("frontend-frameworks", "intermediate", "Svelte", "Keep component state and markup focused on one UI responsibility, and move reusable stateful behavior into a module or shared store when multiple components need it. Treat DOM access and subscriptions as resources that need cleanup. Test reactive updates after both synchronous input and asynchronous completion."),
    ("frontend-frameworks", "advanced", "Next.js", "Choose server rendering for data that can be fetched securely before sending the page, and mark a client boundary only for interactive behavior that needs browser APIs or client state. Never expose server secrets through serialized props. Test the initial server output and subsequent interactive behavior, including loading and error states."),
    ("backend-frameworks", "beginner", "Express", "Order middleware deliberately: request parsing and request identifiers should run before routes, and error middleware should handle failures after routes. Validate request data at the boundary and pass asynchronous errors to the error path. Test malformed input, not-found routes, and errors without returning stack traces to clients."),
    ("backend-frameworks", "intermediate", "FastAPI", "Declare request and response schemas at the endpoint boundary, inject shared dependencies instead of constructing them inside each route, and keep blocking work out of async handlers. Test validation failures, dependency overrides, and response shape. Do not assume that declaring an async function makes synchronous database calls nonblocking."),
    ("backend-frameworks", "intermediate", "Django", "Keep request parsing and permission checks at the view or API boundary, move reusable domain rules into a service or model method, and use database transactions for changes that must succeed together. Test permissions and rollback behavior as well as the successful response."),
    ("backend-frameworks", "intermediate", "Laravel", "Validate untrusted input before using it, authorize the requested action separately from validation, and wrap related database writes in a transaction. Put reusable application rules in a service or action class rather than duplicating them across controllers. Test authorization, validation, and rollback."),
    ("backend-frameworks", "advanced", "Spring", "Use constructor injection for required dependencies so a class's needs are explicit and easy to replace in tests. Put transaction boundaries around application operations that must commit together, and avoid assuming a transaction crosses threads or remote service calls. Test rollback and proxy-related behavior at the integration boundary."),
    ("backend-frameworks", "intermediate", "ASP.NET Core", "Register dependencies with lifetimes that match their state: singleton for safe shared stateless services, scoped for per-request work, and transient for short-lived instances. Pass cancellation tokens through request-bound I/O. Test authorization, cancellation, and that scoped services are not captured by singletons."),
    ("legacy-systems", "intermediate", "COBOL", "Treat a COBOL record layout as an interface contract: document field order, picture clauses, signedness, scale, and encoding before changing it. Add representative input/output fixtures and compare bytes as well as displayed values. Make a migration explicit when packed decimal or fixed-width records cross into a newer service."),
    ("legacy-systems", "beginner", "Fortran", "Declare array bounds and intent explicitly at procedure boundaries, and keep array shape assumptions visible. Check allocation status for allocatable data and avoid relying on implicit interfaces for procedures in separate files. Test lower and upper bounds and zero-length inputs because Fortran arrays need not start at one."),
    ("legacy-systems", "intermediate", "Perl", "Enable strict variable declarations and warnings, then validate input before using it in a regular expression, file path, or command. Use lexical variables and three-argument open calls. Test undefined values and malformed records; warnings reveal bugs but should not replace explicit input validation."),
    ("database-engines", "intermediate", "SQLite", "Use a transaction for a group of writes that must be atomic, and keep one connection's concurrent use serialized unless the selected driver explicitly supports a safe pattern. WAL can improve reader/writer concurrency, but SQLite still permits only one writer at a time. Test locking and recovery with the actual journal mode and filesystem."),
    ("database-engines", "advanced", "PostgreSQL", "Choose a composite index from the query's filter and ordering pattern, then verify it with EXPLAIN ANALYZE on representative data. The leftmost columns affect which predicates can use the index, and every index adds write and storage cost. Compare latency and row estimates before and after; do not infer an index is useful from its existence."),
    ("database-engines", "intermediate", "MySQL", "Use explicit transactions for related InnoDB changes and bind data values through prepared statements. Verify isolation and locking behavior with concurrent transactions, not only a single-session unit test. Keep schema migration and rollback plans for large tables, where a logically simple change can have operational cost."),
    ("database-engines", "advanced", "MongoDB", "Model documents around the read and update patterns, and use schema validation when the application depends on required fields or types. Use a multi-document transaction only when the invariant cannot be maintained by a single-document atomic update; transactions add coordination cost. Test concurrent updates and index use with realistic document sizes."),
    ("mobile-desktop", "intermediate", "Swift", "Keep UI state changes on the UI actor and isolate shared mutable state behind an actor or another synchronization boundary. Propagate task cancellation when a screen disappears, and avoid retaining a view controller from a long-lived task. Test cancellation and concurrent updates, not only the successful response."),
    ("mobile-desktop", "intermediate", "Kotlin", "Use structured concurrency so child coroutines share a lifecycle and cancellation propagates when their owner ends. Keep blocking calls off the main dispatcher and represent loading, success, and failure as explicit UI states. Test cancellation and retry behavior with a controllable fake dependency."),
    ("mobile-desktop", "beginner", "Flutter", "Build UI from state: update the state owner after an action, then let the widget tree render the new value. Dispose controllers, stream subscriptions, and animation resources with their owning state object. Test empty, loading, success, and error states rather than only a screenshot of the happy path."),
    ("mobile-desktop", "advanced", "Tauri", "Treat the webview as an untrusted boundary: expose only the narrow commands the UI needs, validate every command argument in Rust, and restrict origins and capabilities. Do not pass arbitrary shell or filesystem access to front-end code. Test denied capabilities and malformed command input as well as successful IPC."),
    ("build-toolchains", "intermediate", "Cargo", "Commit Cargo.lock for an application so builds use the resolved dependency graph, and review dependency updates rather than treating a successful resolution as a security review. Keep features minimal and run tests with the lockfile enforced. Separate library version ranges from the exact resolution used by the application."),
    ("build-toolchains", "intermediate", "Gradle", "Use the Gradle wrapper so developers and CI run the project's declared Gradle version. Declare dependencies centrally where practical, enable dependency locking or verification for reproducible builds, and run the same test task in CI. Inspect the resolved graph when a transitive upgrade changes behavior."),
    ("build-toolchains", "beginner", "Make", "Declare each target's real file prerequisites and write outputs to named files so Make can skip work only when inputs are unchanged. Mark command-like targets such as clean or test as phony. Test a clean build and an incremental build after changing one source file; missing dependencies can produce stale outputs."),
]

VALID = [
    ("frontend-frameworks", "intermediate", "How would you test a React search box when responses can arrive out of order?", ["abort", "stale", "cleanup"]),
    ("backend-frameworks", "intermediate", "How do you test that a FastAPI route does not block while accessing a synchronous client?", ["blocking", "async", "thread"]),
    ("legacy-systems", "beginner", "What must be preserved when copying a fixed-width COBOL record into a new service?", ["field", "scale", "encoding"]),
    ("database-engines", "advanced", "How can you establish that a PostgreSQL index improves a production-shaped query?", ["explain", "analyze", "write"]),
    ("mobile-desktop", "intermediate", "What should happen to a Kotlin coroutine when its screen owner is destroyed?", ["cancel", "lifecycle", "structured"]),
    ("build-toolchains", "beginner", "Why can a Make target remain stale after one of its source inputs changes?", ["prerequisite", "dependency", "input"]),
]

EVAL = [
    ("frontend-frameworks", "advanced", "angular", "When moving an AngularJS application feature by feature into Angular, what limits migration risk?", [["feature by feature", "vertical", "incremental"], ["test", "regression"]], ["rewrite the entire application"]),
    ("frontend-frameworks", "intermediate", "react", "How should a React screen handle a request that finishes after the user changes routes?", [["abort", "cancel"], ["cleanup", "ignore the stale result", "request id"]], ["ignore cancellation"]),
    ("frontend-frameworks", "beginner", "vue", "In Vue, where should a value derived from reactive state live?", [["computed"]], ["duplicate state"]),
    ("frontend-frameworks", "advanced", "next", "Which Next.js directive marks an interactive component boundary, and when is it needed?", [["use client", "client directive"], ["browser api", "event handler", "interactivity"]], ["useclient hook"]),
    ("backend-frameworks", "intermediate", "express", "What is a safe ordering for Express parsing, routes, and error middleware?", [["middleware"], ["before routes", "before the route"], ["error middleware"]], ["stack trace"]),
    ("backend-frameworks", "intermediate", "fastapi", "Why can synchronous database access inside an async FastAPI route still hurt concurrency?", [["blocks the event loop", "blocking the event loop", "blocking"], ["async database", "asynchronous database", "thread pool", "run_in_threadpool", "nonblocking"]], ["async makes synchronous io nonblocking"]),
    ("backend-frameworks", "advanced", "spring", "What transaction guarantee should you avoid assuming across a remote service call?", [["avoid assuming", "not guaranteed", "no guarantee"], ["remote service", "remote call"]], ["can ensure all transactions are completed successfully"]),
    ("backend-frameworks", "intermediate", "aspnet", "What happens if an ASP.NET Core singleton captures a scoped service?", [["scoped"], ["singleton", "root provider"], ["scope validation", "captive dependency", "lifetime"]], ["transient lifetime causes scope validation"]),
    ("legacy-systems", "intermediate", "cobol", "What record details must a COBOL migration preserve beyond field names?", [["picture clause", "pic clause", "picture"], ["scale", "decimal places"], ["encoding", "packed decimal", "field order"]], ["just rename"]),
    ("legacy-systems", "beginner", "fortran", "Why should a Fortran routine not assume every array begins at index one?", [["lower bound", "bounds"], ["assumed-shape", "dummy argument", "shape"]], ["zero-based"]),
    ("database-engines", "intermediate", "sqlite", "What concurrency limit remains when SQLite uses WAL mode?", [["one writer", "single writer"], ["reader and writer", "readers and a writer", "readers do not block writers"]], ["no concurrency limit", "unlimited writers", "multiple writers"]),
    ("database-engines", "advanced", "postgresql", "What evidence should guide adding a PostgreSQL composite index?", [["explain analyze", "explain (analyze)", "execution plan", "query plan"], ["write cost", "write overhead", "index maintenance", "writes"]], ["index always improves"]),
    ("database-engines", "intermediate", "mongodb", "When should a MongoDB update use a multi-document transaction?", [["single document", "one document"], ["multiple documents", "multi-document"], ["atomicity", "invariant"]], ["every update", "always use a transaction"]),
    ("mobile-desktop", "intermediate", "swift", "Where should shared mutable Swift state be isolated when concurrent tasks access it?", [["actor", "dispatchqueue", "serial queue", "lock"], ["isolate", "synchronization", "protect", "serialize access"]], ["global mutable"]),
    ("mobile-desktop", "intermediate", "kotlin", "What does structured concurrency provide for screen-owned Kotlin work?", [["cancel", "cancellation"], ["lifecycle", "owner", "scope"], ["child", "structured"]], ["detached"]),
    ("mobile-desktop", "advanced", "tauri", "How should a Tauri app expose filesystem behavior to webview code?", [["capabilities", "scope"], ["validate", "validation"], ["narrow", "allowlist", "least privilege"]], ["window.tract", "arbitrary shell"]),
    ("build-toolchains", "intermediate", "cargo", "Why commit Cargo.lock for an application?", [["exact versions", "resolved dependencies", "checksums"], ["reproducible", "repeatable", "consistent"]], ["always use the latest"]),
    ("build-toolchains", "beginner", "make", "What does Make need in a target to rebuild when a source changes?", [["prerequisite", "dependency"], ["source", "input file"]], ["phony only"]),
]


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def encode(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode()


def render() -> dict[str, bytes]:
    train = read_rows(BASE / "train.jsonl")
    for index, (track, level, technology, answer) in enumerate(TRAIN, 1):
        train.append({
            "id": f"ecosystem-{track}-{technology.lower().replace(' ', '-')}-{index}",
            "track": track,
            "level": level,
            "messages": [
                {"role": "user", "content": f"For {technology}, explain a reliable implementation approach and the main failure cases to test."},
                {"role": "assistant", "content": answer},
            ],
        })
    valid = read_rows(BASE / "valid.jsonl")
    for index, (track, level, prompt, terms) in enumerate(VALID, 1):
        valid.append({"id": f"ecosystem-valid-{index}", "track": track, "level": level,
                      "messages": [{"role": "user", "content": prompt},
                                   {"role": "assistant", "content": "Check the relevant boundary, state or lifetime rule, and failure behavior with an isolated test. Verify the behavior against the framework or engine version in use."}]})
    evaluation = read_rows(BASE / "eval.jsonl")
    for track, level, name, prompt, terms, forbidden in EVAL:
        evaluation.append({"id": f"ecosystem-{name}-heldout", "track": track, "level": level,
                           "prompt": prompt, "must_include_any": [term if isinstance(term, list) else [term] for term in terms],
                           "must_not_include": forbidden})
    train_prompts = {row["messages"][0]["content"] for row in train}
    valid_prompts = {row["messages"][0]["content"] for row in valid}
    eval_prompts = {row["prompt"] for row in evaluation}
    require(len({row["id"] for row in train}) == len(train), "duplicate training IDs")
    require(len({row["id"] for row in valid}) == len(valid), "duplicate validation IDs")
    require(len({row["id"] for row in evaluation}) == len(evaluation), "duplicate evaluation IDs")
    require(not train_prompts & valid_prompts, "training and validation prompts overlap")
    require(not train_prompts & eval_prompts, "training and evaluation prompts overlap")
    require(not valid_prompts & eval_prompts, "validation and evaluation prompts overlap")
    return {"train.jsonl": encode(train), "valid.jsonl": encode(valid), "eval.jsonl": encode(evaluation)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    if args.check:
        changed = [name for name, data in outputs.items() if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if changed:
            raise SystemExit("Generated v3 dataset is stale: " + ", ".join(changed))
        print("Committed ecosystem dataset matches its curated source.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    print(f"Wrote {len(outputs['train.jsonl'].splitlines())} training, {len(outputs['valid.jsonl'].splitlines())} validation, and {len(outputs['eval.jsonl'].splitlines())} held-out rubric rows.")


if __name__ == "__main__":
    main()
