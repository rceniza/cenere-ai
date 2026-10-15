#!/usr/bin/env python3
"""Build a small curated, split-safe Cenere curriculum/training benchmark."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "cenere-multistack-v1"

# Each track has one deliberately short supervised example at each stage.
# Keep answers stable and tool/version independent; use live docs for versioned APIs.
TRACKS = [
    ("foundations", [
        ("How should I build a unit converter that rejects invalid and out-of-range input?", "Parse input into a numeric type that can represent the result, then check both syntax and the allowed range before converting. Keep conversion in a pure function. Test a normal value, both boundaries, empty input, nonnumeric input, and overflow."),
        ("Why is a hash map usually better than repeatedly scanning a list for word counts?", "A list scan for each word can take O(n) per lookup, making a full count approach O(n²). A hash map updates the count by key in average O(1), so processing n words is average O(n). Measure on representative data and account for memory use."),
        ("How do I compare two implementations before optimizing one?", "Write correctness tests first, then benchmark both with the same representative inputs and a release build. Record elapsed time and memory, repeat runs, and profile to find the hot path. Include input size and hardware; avoid claiming a speedup from one noisy run."),
    ]),
    ("c", [
        ("In C, how can I parse a whole line as an integer without accepting trailing junk?", "Use `strtol` with `errno` reset and an end pointer. Reject input when no digits were consumed, `errno == ERANGE`, or non-whitespace remains after the number. Check the value against the destination type's limits before casting, and test empty, oversized, and partially numeric strings."),
        ("What must a C resizable vector do when realloc fails?", "Keep the original pointer until `realloc` succeeds: assign its result to a temporary pointer, check for NULL, and only then replace the stored pointer and capacity. On failure, preserve the old vector so callers can still use and free it. Check multiplication overflow before computing the allocation size."),
        ("What should a C TCP echo server do when a client disconnects during send?", "Treat `recv` returning zero as orderly disconnect, retry interrupted calls when appropriate, and handle partial sends by advancing an offset until all bytes are written or an error occurs. Close the client socket on every exit path. Bound clients and test abrupt disconnects; never assume one send writes the whole buffer."),
    ]),
    ("cpp", [
        ("How should I store a changing list of scores in modern C++?", "Use `std::vector<int>` for an ordered, resizable collection and standard algorithms for common operations. Prefer value types and let the vector manage its storage. Check input before insertion and test empty, duplicate, and boundary cases; use a map only when lookup by a separate key is required."),
        ("Why use RAII and `std::unique_ptr` instead of owning raw pointers?", "RAII ties resource lifetime to an object's scope, so cleanup happens on normal return and exceptions. `std::unique_ptr<T>` expresses single ownership and releases the object automatically. Use a raw pointer or reference only as a non-owning view; make ownership transfer explicit with `std::move`."),
        ("What synchronization does a bounded C++ queue need?", "Protect the queue and its closed state with a mutex, and use condition variables with predicate loops for not-empty and not-full conditions. Wake waiters when items arrive, space opens, or shutdown begins. Define whether close drains queued items, and test multiple producers, consumers, and shutdown races."),
    ]),
    ("csharp", [
        ("How do I validate a numeric string in C# without throwing for ordinary bad input?", "Use `int.TryParse` (or the appropriate numeric type) and check its Boolean result before using the parsed value. Then validate business limits separately. This distinguishes malformed input from a valid number outside the allowed range and avoids using exceptions for normal control flow."),
        ("How should an async .NET service cancel parallel requests?", "Pass the caller's `CancellationToken` through each asynchronous operation and use `Task.WhenAll` for independent work. Do not swallow `OperationCanceledException` as an ordinary failure. Test cancellation before work starts, during an awaited operation, and after one peer task fails."),
        ("What belongs in an ASP.NET Core API integration test for authorization?", "Exercise the HTTP endpoint with an unauthenticated identity, an authenticated user lacking the required permission, and an authorized user. Assert status codes and that unauthorized requests cause no side effects. Keep authentication and authorization distinct, and use a test authentication handler instead of production credentials."),
    ]),
    ("php", [
        ("How can a PHP CSV summarizer reject malformed numeric fields?", "Read rows with `fgetcsv`, verify the expected column count, and validate each numeric field before converting it. Do not rely on a loose cast such as `(int)` to detect bad input. Report the row number, skip or reject according to an explicit policy, and test quoted commas and missing fields."),
        ("How do PDO prepared statements prevent SQL injection?", "Prepare SQL with placeholders and bind user values as parameters; never concatenate untrusted values into SQL syntax. Parameters represent values, not table or column names, so dynamic identifiers need a strict allowlist. Test quotes and SQL-looking strings and verify they remain data."),
        ("How do I make a PHP background job safe to retry?", "Give each logical job a stable idempotency key and persist its completion or side effect atomically where possible. Retry only transient failures with bounded exponential backoff and a maximum attempt count. Make duplicate delivery harmless, record terminal failures, and test a crash after the side effect but before acknowledgment."),
    ]),
    ("javascript-typescript", [
        ("When rendering user input in a browser, why prefer `textContent` over `innerHTML`?", "`textContent` inserts the value as text, so markup-like input is not parsed as executable HTML. `innerHTML` parses markup and can create an injection vulnerability. Use DOM APIs and context-appropriate output encoding; test a string containing tags and event-handler text."),
        ("How can TypeScript represent an API result that is either data or an error?", "Use a discriminated union, for example `{ kind: 'ok'; data: Item[] } | { kind: 'error'; message: string }`. Narrow on `kind` before reading variant fields. This makes handled states explicit and lets the compiler flag code that assumes data exists on an error result."),
        ("How should a browser data loader avoid stale responses after a route changes?", "Create an `AbortController` for each request, pass its signal to `fetch`, and abort the previous request during cleanup. Also guard state updates if cancellation is unsupported by a dependency. Test rapid route changes and ensure the older response cannot overwrite the newer view."),
    ]),
    ("nodejs", [
        ("What should a Node.js JSON API validate before using a request body?", "Check the content type, body size, required fields, and field types at the boundary. Return a client error for invalid input and avoid passing unchecked values into storage or shell commands. Test missing fields, wrong types, oversized bodies, and a valid request; keep errors useful without exposing internals."),
        ("How can a Node.js service handle an upstream timeout without an unhandled rejection?", "Set an explicit timeout or abort signal for the outbound request, catch the rejection at the request boundary, and map it to a controlled service error. Release resources in `finally` and avoid retrying non-idempotent work blindly. Test timeout, connection failure, malformed response, and recovery."),
        ("How do idempotency keys prevent duplicate effects in a retryable Node.js job?", "Associate a stable key with the logical operation and atomically record or claim that key with the side effect. A repeated delivery returns the stored outcome instead of repeating the operation. Expire keys only after the retry window and test concurrent duplicate deliveries and a worker crash."),
    ]),
    ("react", [
        ("Why does React need a stable `key` when rendering a list?", "A stable key lets React match each item with its previous component instance when the list changes. Use a persistent item identifier, not the array index when items can be inserted, removed, or reordered. Test reordering to ensure state stays with the correct item."),
        ("How should a React component clean up a request started in an effect?", "Create an `AbortController` inside the effect, pass its signal to the request, and abort it in the cleanup function. Handle abort separately from a user-visible failure. This prevents stale results and updates after unmount; test unmount and fast query changes."),
        ("When should I add `memo` or `useMemo` to a slow React view?", "Measure the view with the React Profiler first and identify repeated work that matters to user-visible latency. Then memoize only the expensive component or calculation with stable dependencies and remeasure. Memoization has its own cost and does not fix slow I/O or an inefficient algorithm."),
    ]),
    ("web-platform", [
        ("What makes a simple HTML page easier to navigate with a keyboard and screen reader?", "Use semantic landmarks, a logical heading order, labels associated with form controls, visible focus, and native buttons and links. Give images useful alternative text when they convey information. Test keyboard-only navigation and inspect the accessibility tree; do not rely on color alone."),
        ("How do I make a card layout adapt to narrow screens?", "Use a flexible grid or flex layout with a content-driven breakpoint, allow items to wrap, and avoid fixed page widths. Set the viewport meta tag and check text zoom and overflow at narrow widths. Verify with browser viewport tests rather than assuming one desktop screenshot proves responsiveness."),
        ("How should a site deploy a Content Security Policy safely?", "Start by inventorying required script, style, image, and connection sources, then test a restrictive policy in report-only mode. Remove inline execution where practical, use nonces or hashes when needed, and review violations before enforcement. A CSP reduces impact; it does not replace output encoding."),
    ]),
    ("python", [
        ("How should a Python function handle a missing or malformed input value?", "Validate at the boundary and raise or return a specific error for invalid input; do not silently coerce malformed data. Keep the normal transformation in a small function and test valid input, missing input, wrong type, and boundary values. Catch exceptions only where the program can recover or add context."),
        ("What is the difference between a Python module and a package?", "A module is an importable Python source file; a package groups modules under a namespace, commonly with a directory and package metadata. Keep public imports deliberate, declare dependencies in project metadata, and test installation from a clean environment rather than relying on the repository working directory."),
        ("When does `asyncio` help a Python HTTP service, and when does it not?", "Async I/O helps when many tasks spend time waiting on nonblocking network or disk operations. It does not make CPU-bound Python work parallel by itself; use processes, native code, or a worker system for CPU-heavy tasks. Bound concurrency, set timeouts, and test cancellation and backpressure."),
    ]),
    ("rust", [
        ("How do I parse a Rust line as a signed 64-bit integer?", "Call `line.trim().parse::<i64>()` and handle the returned `Result<i64, ParseIntError>` with `match` or `?` in a function returning `Result`. Keep parse errors distinct from later range or business-rule errors, and test empty, invalid, minimum, and maximum values."),
        ("What does Rust ownership prevent when passing a string to a function?", "Ownership ensures one value has one owner at a time, while borrowing lets a function inspect a value through `&T` without taking ownership. Use `&str` for read-only string input when possible; use `&mut T` for exclusive mutation. The compiler checks references do not outlive their data."),
        ("What should I review before using `unsafe` in a Rust parser?", "First try safe APIs. If `unsafe` is necessary, state the exact invariant each unsafe operation relies on, keep the block small, and expose a safe wrapper that enforces those preconditions. Test malformed and boundary inputs, run Miri where applicable, and document why aliasing and validity rules hold."),
    ]),
    ("go-java", [
        ("How should Go and Java code report a failed operation to its caller?", "In Go, return an `error` alongside the result and check it explicitly; add context with `%w` when callers may need `errors.Is` or `errors.As`. In Java, use a suitable exception or result type and preserve the cause. In both, avoid logging and discarding an error that the caller must handle."),
        ("What is a safe way to share work across concurrent Go goroutines or Java threads?", "Define who owns each piece of mutable state. Prefer message passing or immutable values; otherwise protect shared mutation with a mutex or a concurrency-safe abstraction. Bound worker counts and propagate cancellation. Test races and shutdown; do not assume launching more goroutines or threads increases throughput."),
        ("How do I investigate high memory use in a Go or Java service?", "Capture a representative workload and profile allocations before changing code. Use Go pprof or Java Flight Recorder/heap tools, identify retained objects and allocation hot spots, then change one cause and compare the same workload. Include latency and garbage-collection behavior; do not infer a leak from one memory snapshot."),
    ]),
    ("backend-api", [
        ("Which HTTP status should a JSON API return when it creates a resource?", "For a successful creation, return `201 Created` and identify the new resource, commonly with a `Location` header. Use `400 Bad Request` or a documented validation status for invalid input, and do not report success before the write commits. Test both status and response body."),
        ("What is the difference between authentication and authorization?", "Authentication establishes who the caller is; authorization decides whether that identity may perform a specific action on a specific resource. Check authorization on every protected operation, including object IDs supplied by the caller. Test anonymous, wrong-owner, insufficient-role, and permitted requests."),
        ("How can an API make retries safe when a client times out after a write?", "Use an idempotency key scoped to the caller and operation, persist it with the result in the same transaction as the side effect, and return that result for retries. Define key retention and payload mismatch behavior. Test a lost response and concurrent identical requests."),
    ]),
    ("sql-data", [
        ("How can I prevent a SQL query from treating user input as SQL syntax?", "Use parameterized queries or prepared statements so input is bound as a value, not concatenated into SQL. Add database constraints for invariants that must hold regardless of caller. For identifiers that cannot be parameters, choose them from a fixed allowlist."),
        ("Why should related database writes use a transaction?", "A transaction makes a group of related changes commit together or roll back together, preserving invariants when one step fails. Keep it short, handle errors, and choose isolation based on the anomalies the application must prevent. Test failure between writes and concurrent updates."),
        ("How do I decide whether a SQL index will improve a slow query?", "Inspect the query plan and measure with representative data before adding an index. Index columns used by selective filters or joins, considering order for composite indexes. Every index costs storage and slows writes; remeasure query latency and write performance after the change."),
    ]),
    ("git-linux-shell", [
        ("How do I make a shell pipeline fail if an earlier command fails?", "In Bash, enable `set -o pipefail` so a pipeline returns a failing status when a command before the last one fails. Use explicit checks for important operations and quote variable expansions. Test a deliberately failing first command; `set -e` alone has context-dependent behavior."),
        ("How can I recover a file from an earlier Git commit without resetting all work?", "Use `git restore --source=<commit> -- path/to/file` to copy that path from the chosen commit into the working tree, then inspect the diff before committing. Check `git status` first and keep unrelated changes. Avoid `reset --hard` unless intentionally discarding the whole worktree state."),
        ("How should a production shell job handle signals and temporary files?", "Install traps for expected termination signals and cleanup, use a private temporary directory with restrictive permissions, and ensure cleanup is idempotent. Quote paths and avoid evaluating untrusted strings as shell code. Test normal exit, command failure, and interruption in an isolated environment."),
    ]),
    ("docker", [
        ("What is the difference between a Docker image and a container?", "An image is an immutable set of filesystem layers and metadata used as a template. A container is a running or stopped instance with its own process and writable layer. Persist important data in a volume, pass configuration explicitly, and do not assume container filesystem changes update the image."),
        ("How do Docker Compose volumes differ from a container's writable layer?", "A named volume persists independently of a container and can be reused after replacement. The writable layer belongs to that container and is lost when it is removed. Mount only the data that needs persistence, document backup/restore, and test container recreation."),
        ("What hardening should I apply before publishing a production container?", "Run as a non-root user, use a small pinned base image, keep secrets out of image layers, and include only runtime dependencies. Scan and record the image digest, use a read-only filesystem where feasible, and test required writable paths and graceful shutdown."),
    ]),
    ("cicd", [
        ("What should a beginner CI workflow run on a pull request?", "Run formatting or lint checks, unit tests, and a reproducible build for the changed project. Fail the check when any required step fails and keep logs/artifacts useful for review. Treat a green test suite as evidence for those checks, not proof that production behavior is perfect."),
        ("How should a deployment pipeline protect production secrets?", "Use a protected environment with least-privilege, short-lived credentials where supported, and limit which branches or reviewers can deploy. Do not print secrets or place them in artifacts. Prefer workload identity/OIDC over long-lived keys and audit who can approve production."),
        ("What evidence makes a release artifact traceable and rollbackable?", "Build an immutable artifact from a known commit, record its digest and provenance, and promote that same artifact between environments. Keep the prior known-good version available and define health checks and rollback triggers. Test rollback in a nonproduction environment."),
    ]),
    ("kubernetes", [
        ("What is the difference between a Kubernetes Deployment and a Service?", "A Deployment manages the desired replica count and rollout of Pods. A Service provides a stable network name and routes traffic to matching ready Pods. Verify labels/selectors match, then inspect endpoints and events when traffic does not reach the application."),
        ("How are Kubernetes readiness and liveness probes different?", "Readiness controls whether a Pod should receive Service traffic; liveness indicates whether Kubernetes should restart a stuck container. A dependency outage should not automatically fail liveness and trigger restart loops. Set realistic initial delays and test startup, degraded dependency, and recovery."),
        ("What should an HPA and disruption budget account for in a production workload?", "An HPA needs meaningful resource requests and a metric that tracks capacity pressure; it cannot scale usefully from an unconfigured or misleading signal. A disruption budget limits voluntary simultaneous disruption but does not guarantee application availability. Test scaling and node maintenance under realistic load."),
    ]),
    ("kafka-redpanda", [
        ("What ordering guarantee does a Kafka partition provide?", "Records are ordered within a single partition, not across all partitions in a topic. Choose a stable key when related events must stay ordered, and avoid putting every event under one key if that creates a hot partition. Test ordering and distribution with representative keys."),
        ("What happens when a consumer group has more consumers than partitions?", "A partition is assigned to at most one consumer in a group at a time, so extra consumers remain idle until partitions or groups change. Adding partitions can change key-to-partition mapping. Monitor lag and rebalance behavior rather than assuming more consumers always add throughput."),
        ("How do I make a Kafka consumer's external database write safe under redelivery?", "Assume at-least-once delivery can repeat a record. Make the database side effect idempotent using a stable event ID and commit the consumed offset only after durable processing. If the database and broker cannot share a transaction, design for replay and test a crash between write and offset commit."),
    ]),
    ("caching", [
        ("What is the cache-aside pattern?", "The application checks the cache first, loads from the source on a miss, then stores the result with an expiration. On writes, update or invalidate the corresponding cache key so stale values are bounded. Measure hit rate and latency; cache only data that can tolerate the chosen staleness."),
        ("How can an application reduce a cache stampede for one popular key?", "Coalesce concurrent misses so one request refreshes the key while others wait or use a bounded stale value. Add jitter to expirations and limit refresh concurrency. Keep a timeout and fallback path; test a cold cache under simultaneous requests and verify the source is not flooded."),
        ("What should happen when Redis is unavailable?", "Choose explicitly whether each operation can fail open to the source or must fail closed for correctness/security. Bound connection and retry time, use a circuit breaker or backoff, and avoid turning a cache outage into unbounded source load. Test stale data and recovery behavior."),
    ]),
    ("observability-sre", [
        ("What is a useful structured log entry for an API request?", "Include a request or trace ID, route, outcome, duration, and a stable error category. Exclude passwords, tokens, and unnecessary personal data. Use consistent field names and test that failures can be correlated without relying on free-form message text."),
        ("What is the difference between a metric and a trace?", "A metric aggregates numerical behavior over time, such as request rate or latency distribution. A trace follows one request across operations and services. Use metrics for trends and alerting, traces for individual paths, and control high-cardinality labels to avoid runaway storage."),
        ("How should an SLO alert be tied to an error budget?", "Define the user-facing success event, measurement window, and target before alerting. Alert on a meaningful burn rate that gives responders time to act, not every isolated failure. Link the alert to a runbook and review false positives and missed incidents after use."),
    ]),
    ("security", [
        ("What is the safest general way to prevent SQL injection?", "Use prepared statements with bound parameters and avoid building SQL from untrusted strings. Validate values for business rules as well, and allowlist dynamic identifiers such as sort columns. Add tests with quote characters and SQL-looking input to verify it remains data."),
        ("Why should authorization be checked on every object access?", "A valid login proves identity, not permission to read or modify every object. Check the caller's role and ownership or tenant scope on each operation, including by-ID endpoints. Test cross-user access and ensure denial occurs before a side effect or sensitive response."),
        ("What belongs in a threat model for a new web service?", "Identify valuable assets, actors, entry points, trust boundaries, and likely abuse cases, then map mitigations and residual risks. Include authentication, data access, dependencies, deployment secrets, and recovery. Revisit it when architecture or exposed interfaces change."),
    ]),
    ("cloud-production", [
        ("What do DNS and TLS each do when a browser connects to a service?", "DNS resolves a name to network records; TLS authenticates the server certificate and protects the connection in transit. Correct DNS does not prove the endpoint is secure. Check certificate hostname, expiration, and renewal, and avoid sending secrets over plaintext HTTP."),
        ("How should a team roll back a bad production deployment?", "Keep the last known-good immutable artifact and configuration available. Define health checks and rollback criteria, then route traffic back while preserving logs and database compatibility. Test rollback before an incident; schema changes often need an expand-and-contract migration."),
        ("What should a disaster recovery exercise verify beyond that backups exist?", "Restore a backup into an isolated environment and verify data integrity and application behavior. Measure recovery time and data loss against the RTO and RPO, and document credentials and dependencies needed for restore. A successful backup job alone does not prove recoverability."),
    ]),
    ("ai-model-ops", [
        ("Why does a local language model still use RAM when chat history is stored in SQLite?", "SQLite keeps durable history on disk, but inference still loads model weights and the active prompt into memory. Retrieve only relevant notes and a bounded recent history, then compact older turns into a summary. This reduces prompt memory; it does not eliminate model runtime memory."),
        ("How should I compare an adapter with the base model?", "Use the same fixed prompts, decoding settings, and held-out examples for both. Score task correctness with explicit checks and run code examples through their compiler or tests. Record model, adapter, dataset, and score; reject an adapter that improves training loss but regresses held-out behavior."),
        ("What makes local LoRA training safer on a memory-limited Mac?", "Start with reviewed examples, batch size one, a small number of trainable layers, and a short iteration count. Check memory pressure and stop if the system begins heavy swapping. Save an adapter candidate, evaluate it against the unchanged base, and do not replace the served model on loss alone."),
    ]),
    ("multimodal", [
        ("Can the installed Qwen2.5-Coder model inspect a raw image?", "No. The installed checkpoint is a text-only `Qwen2ForCausalLM`, and this chat endpoint accepts string content without image payloads. A user-provided description or OCR text can be discussed as text, but that is not visual inspection. Image input needs a vision-language checkpoint, processor, and compatible serving pipeline."),
        ("What should an image-question benchmark record to prevent unsupported claims?", "Store the image, question, expected visible evidence, acceptable answer, and claims that must not be made. Score whether the answer is grounded in the image and whether uncertainty is stated when details are unreadable. OCR output alone should be evaluated separately from visual reasoning."),
        ("How could a video workflow provide temporal evidence to a vision model?", "Decode a short clip into timestamped frames at a documented sampling rate and send them through a video-capable processor. Ask the model to cite timestamps for events and score missed or invented events. This current text-only checkpoint and endpoint cannot consume raw video or frames as images."),
    ]),
]

VALID = [
    ("foundations", "beginner", "Why test both ordinary and boundary inputs?", "Ordinary cases check expected behavior; boundary and invalid cases reveal off-by-one errors, overflow, and missing validation. Keep each case reproducible and assert the result, not just that the program did not crash."),
    ("c", "intermediate", "Why should an owning C function document who frees its returned pointer?", "C does not track ownership automatically. State whether the caller or callee owns the allocation, how long it remains valid, and which function releases it. Clear ownership rules prevent leaks, double frees, and use-after-free errors."),
    ("cpp", "beginner", "When is `std::map` more appropriate than `std::vector`?", "Use a map when values are associated with keys and ordered key lookup is useful. Use a vector for a sequence indexed by position. Choose from access patterns and measure; a container is not faster merely because its name sounds specialized."),
    ("csharp", "intermediate", "Why should an async method accept a cancellation token?", "The caller can stop work when a request is abandoned or a deadline expires. Pass the token to cancellable operations and handle cancellation distinctly from faults so resources are released and shutdown remains responsive."),
    ("php", "beginner", "Why validate CSV column counts before processing a row?", "Rows can be malformed or incomplete, and indexing missing columns may produce incorrect data or warnings. Check the expected shape, report the row number, and define whether the file should reject or skip a bad row."),
    ("javascript-typescript", "intermediate", "Why should a fetch request have a timeout or cancellation policy?", "A network request can remain pending after the user changes pages or abandons the action. Use an abort signal and handle cancellation separately; also provide a visible loading and error state."),
    ("nodejs", "beginner", "When should a Node.js API return 400 instead of 500?", "Use a client error such as 400 when the request is malformed or violates validation. Use 500 for an unexpected server failure. Keep internal stack traces in protected logs, not in the response."),
    ("react", "beginner", "What should a searchable React list render when there are no matches?", "Render an explicit empty state that explains no results were found and lets the user change or clear the query. Keep it accessible and test it through visible text, not internal component state."),
    ("web-platform", "intermediate", "Why must form controls have programmatic labels?", "A label gives assistive technology the control's purpose and enlarges the clickable target when associated correctly. Placeholder text is not a reliable substitute. Verify the accessible name and keyboard focus."),
    ("python", "intermediate", "Why put a Python project in an installable package?", "Packaging defines imports and dependencies consistently so tests and users do not depend on the current working directory. Verify installation in a clean environment and test the documented entry point."),
    ("rust", "intermediate", "Why return a typed error instead of calling `unwrap` in library code?", "A typed `Result` lets the caller decide how to recover and preserves the failure cause. `unwrap` may panic and removes that choice. Use it only where failure is impossible by construction or in a test."),
    ("go-java", "beginner", "Why should a Java or Go build be repeatable on a clean checkout?", "A clean build exposes undeclared dependencies and local machine assumptions. Commit the appropriate dependency metadata and build files, then verify the documented command in CI."),
    ("backend-api", "intermediate", "Why is checking a user role alone sometimes insufficient?", "The user may have the role but not access to the specific tenant or object. Apply object-level authorization on the requested resource and test cross-tenant IDs."),
    ("sql-data", "intermediate", "What does `EXPLAIN` help you inspect?", "It shows the database's chosen query plan, including scans and index use. Compare the plan and actual timings on representative data before adding an index."),
    ("git-linux-shell", "intermediate", "Why inspect `git status` before applying a recovery command?", "It reveals uncommitted changes that a broad reset or checkout could discard. Prefer restoring only the intended path and inspect the resulting diff before committing."),
    ("docker", "beginner", "Where should a container write data that must survive replacement?", "Use a Docker volume or an explicitly managed bind mount. The container's writable layer belongs to that container and should be treated as disposable."),
    ("cicd", "intermediate", "Why should deployment credentials be scoped to an environment?", "Environment protection limits which workflow runs can access production credentials and permits review gates. Grant only the required permissions and avoid long-lived secrets where short-lived identity is available."),
    ("kubernetes", "intermediate", "What does a readiness probe change?", "It controls whether a Pod is considered ready to receive Service traffic. A failed readiness probe removes it from eligible endpoints without necessarily restarting the container."),
    ("kafka-redpanda", "intermediate", "When should a consumer commit an offset?", "After the record's durable side effect succeeds, unless a carefully designed transaction coordinates both systems. Delayed commits can cause replay, so make processing idempotent."),
    ("caching", "beginner", "What does a cache TTL guarantee?", "It bounds how long that cached entry is retained before expiration; it does not guarantee the source remains unchanged or that all clients see identical data. Choose a TTL based on acceptable staleness."),
    ("observability-sre", "beginner", "Why should logs avoid credentials and tokens?", "Logs are often copied to systems with broader access and longer retention. Redact secrets at the source and test representative failures to ensure sensitive values are not emitted."),
    ("security", "intermediate", "What is least privilege?", "Give each user, service, or workflow only the permissions required for its task and duration. Review inherited access and test that forbidden actions fail."),
    ("cloud-production", "advanced", "Why record both RTO and RPO?", "RTO is the target time to restore service; RPO is the maximum acceptable data loss measured in time. Backup and replication design must be tested against both targets."),
    ("ai-model-ops", "beginner", "Why keep evaluation prompts out of the training split?", "If evaluation examples are used for optimization, the score no longer estimates generalization. Keep a fixed held-out set and record its provenance."),
    ("multimodal", "advanced", "Can sampling video frames make a text-only model video-capable?", "No. Frame extraction creates images, but the model and serving pipeline still need vision support to interpret them. A text-only model can only process descriptions or OCR text supplied as text."),
]

EVAL = [
    ("foundations", "beginner", "Explain a robust way to validate a unit-converter input and what to test.", [["parse", "convert"], ["boundary", "range"], ["invalid", "nonnumeric"]], ["ignore all errors", "always return zero"]),
    ("c", "intermediate", "Explain safe realloc handling for a C dynamic array, including failure.", [["temporary", "temp"], ["realloc"], ["original pointer", "old pointer"], ["overflow", "size overflow"]], ["overwrite the only pointer before checking", "free the original pointer on realloc failure"]),
    ("cpp", "advanced", "Describe synchronization and shutdown for a bounded concurrent C++ queue.", [["mutex"], ["condition variable", "condition_variable"], ["predicate", "while"], ["shutdown", "close"]], ["volatile makes it thread-safe"]),
    ("csharp", "beginner", "Show the principle for parsing user-provided integers safely in C#.", [["TryParse", "tryparse"], ["range", "business rule"]], ["parse and ignore exceptions"]),
    ("php", "intermediate", "Explain safe SQL writes in PHP with PDO.", [["prepared", "prepare"], ["parameter", "bind"], ["concatenate", "allowlist"]], ["concatenate user input into sql"]),
    ("javascript-typescript", "intermediate", "Explain how to model success and failure states with a TypeScript discriminated union.", [["discriminated union", "union"], ["kind", "tag"], ["narrow", "narrowing"]], ["use any as a shortcut"]),
    ("nodejs", "beginner", "List boundary checks for a Node.js JSON API request.", [["content type", "content-type"], ["size", "body size"], ["validate", "validation"], ["400", "client error"]], ["trust the body without validation"]),
    ("react", "beginner", "Explain why React list keys need to be stable and when indexes are unsafe.", [["stable", "persistent"], ["index", "array index"], ["reorder", "reordering"]], ["random key"]),
    ("web-platform", "beginner", "Give three ways to make an HTML form usable with keyboard and screen readers.", [["label"], ["focus", "keyboard"], ["semantic", "accessible name"]], ["placeholder is the label"]),
    ("python", "advanced", "Explain when asyncio helps and what to use for CPU-bound work.", [["io", "i/o"], ["cpu-bound", "cpu bound"], ["process", "processes"]], ["asyncio makes cpu work parallel"]),
    ("rust", "beginner", "How do you parse a Rust string as i64 and handle invalid input?", [["parse::<i64>", "i64"], ["result", "error"]], ["parse::<i32>"]),
    ("go-java", "intermediate", "Compare explicit error handling in Go and Java without discarding failures.", [["go", "error"], ["java", "exception"], ["caller", "cause"]], ["ignore the error"]),
    ("backend-api", "intermediate", "Distinguish authentication from object-level authorization and say what to test.", [["identity", "authentication"], ["authorization", "permission"], ["owner", "tenant"], ["cross", "wrong-owner"]], ["login means all resources are accessible"]),
    ("sql-data", "advanced", "Explain when to add a database index and its tradeoff.", [["query plan", "explain"], ["measure", "representative"], ["write", "storage"]], ["index every column"]),
    ("git-linux-shell", "intermediate", "How do you make a Bash pipeline fail when an earlier command fails?", [["pipefail", "set -o pipefail"], ["exit status", "status"]], ["set -e always catches every pipeline failure"]),
    ("docker", "advanced", "Name production Docker image hardening steps and how to verify them.", [["non-root", "nonroot"], ["secrets", "secret"], ["digest", "pinned"], ["read-only", "read only"]], ["put secrets in the image"]),
    ("cicd", "advanced", "Explain how to make a release traceable and rollbackable.", [["commit", "revision"], ["digest", "immutable"], ["rollback", "known-good"]], ["rebuild a different artifact during rollback"]),
    ("kubernetes", "intermediate", "Distinguish readiness and liveness probes and one failure mode to avoid.", [["traffic", "readiness"], ["restart", "liveness"], ["dependency", "restart loop"]], ["use liveness to restart on every dependency outage"]),
    ("kafka-redpanda", "advanced", "Explain safe offset commits when a consumer writes to an external database.", [["idempotent", "idempotency"], ["durable", "write"], ["offset", "commit"]], ["commit before the side effect without replay handling"]),
    ("caching", "advanced", "Describe how to handle Redis outage without overwhelming the source database.", [["bounded", "limit"], ["backoff", "circuit"], ["fallback", "fail open", "fail closed"]], ["retry immediately forever"]),
    ("observability-sre", "intermediate", "Explain how metrics and traces complement each other and mention cardinality.", [["metric", "metrics"], ["trace", "traces"], ["cardinality", "high-cardinality"]], ["put user IDs in every metric label"]),
    ("security", "advanced", "List key elements of a threat model for a web service.", [["asset", "assets"], ["trust boundary", "entry point"], ["abuse", "threat"], ["mitigation", "risk"]], ["only list vulnerabilities after launch"]),
    ("cloud-production", "intermediate", "Explain how to plan rollback when a deployment includes a database schema change.", [["backward compatible", "expand"], ["rollback", "known-good"], ["migration", "schema"]], ["assume database changes always roll back with code"]),
    ("ai-model-ops", "advanced", "How should a low-resource LoRA candidate be evaluated before serving it?", [["held-out", "evaluation set"], ["base model", "baseline"], ["regression", "correctness"], ["memory", "pressure"]], ["promote based only on training loss"]),
    ("multimodal", "beginner", "Can the installed text-only Qwen2.5-Coder inspect an image or video? Explain the missing components.", [["text-only", "qwen2forcausallm"], ["vision", "vision-language"], ["processor", "image payload"], ["video", "frames"]], ["yes, because OCR is automatic"]),
]


def render_jsonl(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode("utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def render() -> dict[str, bytes]:
    tracks = json.loads((ROOT / "curriculum/catalog.json").read_text())["tracks"]
    track_ids = {track["id"] for track in tracks}
    require(len(TRACKS) == len(track_ids) == len({item[0] for item in TRACKS}), "track source has duplicate or missing entries")
    require({item[0] for item in TRACKS} == track_ids, "training source must cover each catalog track exactly once")
    require({item[0] for item in VALID} == track_ids, "validation source must cover every catalog track")
    require({item[0] for item in EVAL} == track_ids, "evaluation source must cover every catalog track")
    train_rows = []
    for track, examples in TRACKS:
        require(len(examples) == 3, f"{track} must have one example at each stage")
        for level, (prompt, answer) in zip(("beginner", "intermediate", "advanced"), examples):
            train_rows.append({
                "id": f"{track}-{level}-core",
                "track": track,
                "level": level,
                "messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}],
            })
    valid_rows = [
        {"id": f"{track}-{level}-heldout", "track": track, "level": level,
         "messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]}
        for track, level, prompt, answer in VALID
    ]
    eval_rows = [
        {"id": f"{track}-{level}-eval", "track": track, "level": level, "prompt": prompt,
         "must_include_any": groups, "must_not_include": forbidden}
        for track, level, prompt, groups, forbidden in EVAL
    ]
    require(len(train_rows) == 75 and len(valid_rows) == len(eval_rows) == 25, "dataset split sizes changed unexpectedly")
    all_prompts = [row["messages"][0]["content"] for row in train_rows + valid_rows]
    require(len(all_prompts) == len(set(all_prompts)), "train/valid prompts must not overlap")
    eval_prompts = {row["prompt"] for row in eval_rows}
    require(not eval_prompts.intersection(all_prompts), "evaluation prompts must be held out")
    require({row["track"] for row in train_rows} == track_ids, "training is missing a catalog track")
    require({(row["track"], row["level"]) for row in train_rows} == {
        (track, level) for track in track_ids for level in ("beginner", "intermediate", "advanced")
    }, "training must cover all three stages for each track")
    require({row["level"] for row in eval_rows} == {"beginner", "intermediate", "advanced"}, "evaluation must cover all three stages")
    return {
        "train.jsonl": render_jsonl(train_rows),
        "valid.jsonl": render_jsonl(valid_rows),
        "eval.jsonl": render_jsonl(eval_rows),
    }


def build() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    outputs = render()
    for filename, content in outputs.items():
        (OUT / filename).write_bytes(content)
    print(f"Wrote {len(outputs['train.jsonl'].splitlines())} training, {len(outputs['valid.jsonl'].splitlines())} validation, and {len(outputs['eval.jsonl'].splitlines())} rubric-evaluation examples across {len(TRACKS)} tracks.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed outputs differ from generated data")
    args = parser.parse_args()
    if args.check:
        outputs = render()
        changed = [name for name, content in outputs.items() if not (OUT / name).is_file() or content != (OUT / name).read_bytes()]
        if changed:
            raise SystemExit("Generated dataset is stale: " + ", ".join(changed))
        print("Committed curriculum dataset matches its source.")
    else:
        build()


if __name__ == "__main__":
    main()
