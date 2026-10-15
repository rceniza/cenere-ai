#!/usr/bin/env python3
"""Extend the problem-solving curriculum with evidence-led engineering scenarios."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "cenere-problem-solving-v1"
OUT = ROOT / "cenere-problem-solving-v2"

TRAIN = [
    ("Debugging", "A Node service starts locally but exits in its container with `ECONNREFUSED` for Redis. What do you inspect before changing retry logic?", "Read the full error and container logs, then inspect the Compose service name, network, port, startup health check, and the URL the application actually uses. Inside a container, localhost refers to that container; use the Redis service DNS name on the shared network. Confirm Redis is healthy and the configured port is reachable, make readiness explicit if startup order is the cause, then rebuild and verify the service can reconnect after a restart. Add a startup integration test or health check that covers the failure."),
    ("Concurrency", "Two workers consume the same queue message and both charge a customer. How should the system prevent a duplicate charge?", "Treat delivery as at least once and assume the handler can run concurrently. Require a stable payment idempotency key, enforce it with a durable uniqueness constraint at the payment boundary, and return the original result for a duplicate request. Do not rely on an in-memory lock or queue visibility timeout as the correctness guarantee. Test simultaneous deliveries, retries after a timeout, and a crash after the charge succeeds but before acknowledgment."),
    ("Database migration", "A migration renames a column, but old and new application instances overlap during deployment. How do you make the rollout safe?", "Use an expand-and-contract rollout. First add the new representation without removing the old one, deploy code that can read both and writes compatibly, backfill and verify data, and only then deploy code that stops using the old column. Remove it in a later release after confirming no old instances remain. Test migration ordering, rollback limits, and mixed-version reads against a production-like copy; do not assume a destructive rename is backward compatible."),
    ("Memory investigation", "A worker's memory grows over hours. Restarting it temporarily helps. What evidence should guide a fix?", "Capture a baseline and time series for resident memory, heap, request volume, queue depth, and object or allocation profiles. Compare snapshots after representative workloads and identify retained objects or unbounded buffers. Reproduce with a bounded load test, fix the retention or apply an explicit bounded queue/backpressure policy, then run the same workload and confirm memory plateaus without dropped work or changed results. Treat a scheduled restart as mitigation, not proof of the leak's cause."),
    ("Frontend diagnosis", "A page displays different server and browser content and logs a hydration mismatch. What do you check first?", "Inspect the exact mismatch and identify values rendered differently between server and browser, such as current time, locale, randomness, browser-only state, or invalid HTML nesting. Keep the initial render deterministic and move browser-dependent behavior into an effect or an explicit client boundary. Do not silence the warning before understanding it. Add a test for the first render and verify the page after hydration with the relevant locale and route."),
    ("Security and dependencies", "A dependency scanner reports a critical package issue, but the advisory names several affected versions. What should the agent do?", "Identify the exact direct or transitive package and locked version from the project lockfile, then verify the advisory's affected range and fixed version from the maintainer or registry advisory. Check whether the vulnerable code path is reachable, but do not treat reachability as a substitute for upgrading when a safe fix exists. Choose the smallest compatible patched version, update the lockfile, run focused tests and the full relevant suite, and report any breaking upgrade or unresolved exposure."),
    ("Kubernetes incident", "A rollout is stuck because new pods fail readiness while the old pods are still serving. What is a safe triage sequence?", "Inspect rollout status, pod events, readiness probe output, container logs, and recent image/configuration changes. Compare a failing pod with a healthy old pod and verify the readiness endpoint reflects actual ability to serve. If users are affected, use the documented rollout undo or pause procedure and verify recovery; do not delete resources blindly. Reproduce the startup failure, fix the cause, and confirm the new revision becomes ready before allowing rollout to continue."),
    ("Performance diagnosis", "A SQL endpoint is slow only for one tenant with a very large dataset. What do you inspect before adding an index?", "Capture the slow query and parameters, inspect the query plan and existing indexes, and measure rows scanned, cardinality, lock waits, and database load for both large and typical tenants. Check whether the query is tenant-scoped and whether parameter-sensitive plans or skew explain the difference. Propose an index only with its write/storage cost understood, test representative data and concurrent writes, and compare latency and plan changes before and after."),
    ("Kafka correctness", "A consumer commits its offset before writing to a database; a crash can lose an update. What is the failure and a safer pattern?", "Committing first creates a loss window: the broker considers the message complete even if the database write never commits. Process the record, durably commit an idempotent database effect, then commit the offset; a crash between those steps can redeliver, so deduplicate by a stable event ID or use an inbox/unique constraint. Test crashes at each boundary and monitor lag and duplicate handling. Do not claim independent Kafka and SQL commits are atomic."),
    ("CI diagnosis", "A test becomes flaky after parallel CI was enabled, and it uses a fixed temporary filename. What is the likely cause and how do you verify it?", "Parallel jobs may be sharing the same path and overwriting each other's fixtures. Inspect the failing job IDs and filesystem traces, then run the test concurrently with isolated temporary directories and unique names. Fix the test to create per-run temporary state with cleanup, not by serializing the entire suite unless shared state is intentional. Repeat the focused test under parallel load and then run the relevant suite."),
    ("API design", "A client retries a timed-out POST, and the server may have completed the first request. How should the API handle this ambiguity?", "Define a client-supplied idempotency key scoped to the operation and principal, persist the key with the result atomically, and return the stored result on retries. Reject reuse of a key with a different request body. Document retention and expiry semantics and distinguish a timeout from a confirmed failure. Test concurrent duplicate requests and a server crash around the commit boundary; a client-side retry alone cannot make the operation safe."),
    ("Infrastructure planning", "A production config change looks small but could affect every replica. How should a coding agent stage and verify it?", "Inspect the current config source, deployment mechanism, blast radius, and rollback path. Validate syntax and policy locally, then apply to a canary or limited replica set using the documented workflow. Watch the relevant health, error, and resource signals against a baseline before expanding. Stop or roll back if the agreed threshold is crossed, and verify the previous behavior is restored. Do not run an unreviewed cluster-wide command based only on the apparent size of the diff."),
]

VALID = [
    ("Why can `localhost:6379` work from a developer machine but fail from an application container?", "Inside the container localhost refers to that container. Use the Redis service DNS name on the shared container network and verify service health and port configuration."),
    ("A webhook is delivered twice after a slow response. What prevents duplicate business effects?", "Use a stable delivery/event ID with a durable unique constraint or inbox, make the effect idempotent, and test concurrent delivery and retry after a crash."),
    ("Why is a one-step destructive schema rename risky while two application versions are live?", "The old version may still read/write the old column. Expand first, deploy backward-compatible code, backfill and verify, then contract after old instances are gone."),
    ("A service's RSS grows after each batch but the heap snapshot is flat. What else can explain it?", "Inspect native allocations, memory-mapped buffers, allocator behavior, and process-level metrics over a representative workload; compare snapshots and verify whether RSS plateaus."),
    ("A Kubernetes pod is running but never ready. Which evidence distinguishes application startup failure from a bad probe?", "Compare pod events and probe output with container logs and the actual readiness endpoint; verify path, port, timing, and that readiness represents serving capability."),
    ("What ordering avoids losing a database effect when consuming a Kafka record, and why can duplicates still happen?", "Commit the idempotent database effect before committing the offset. A crash between those commits can redeliver, so deduplicate by event ID or an inbox constraint."),
]

EVAL = [
    ("container-network", "A web process in a container cannot reach a database at `localhost:5432`, though the database container is healthy. What should be checked and changed?", [["localhost refers", "inside the container", "container localhost"], ["service name", "dns name", "service dns"], ["network", "shared network"]], ["disable the firewall", "use host networking without evidence"]),
    ("duplicate-payment", "A queue redelivers an event while its first handler is still running. How do you prevent two charges?", [["idempotency key", "stable event id"], ["unique constraint", "durable deduplication", "inbox"], ["concurrent", "simultaneous", "retry"]], ["in-memory lock is sufficient", "visibility timeout guarantees exactly once"]),
    ("mixed-version-migration", "A destructive database change is proposed during a rolling deployment with mixed application versions. What rollout strategy avoids breaking old instances?", [["expand", "additive"], ["backward compatible", "both versions", "old and new"], ["backfill", "verify"], ["contract", "remove later"]], ["rename immediately", "drop column first"]),
    ("memory-growth", "A worker's RSS rises after each batch. What would distinguish a leak from normal allocator behavior, and how would you verify a fix?", [["baseline", "time series", "representative workload"], ["profile", "snapshot", "retained"], ["plateau", "same workload", "regression test"]], ["restart proves fixed", "increase memory limit only"]),
    ("hydration-mismatch", "A server-rendered screen shows a hydration warning after adding a timestamp. What should be investigated and changed?", [["server and browser", "initial render", "different output"], ["time", "nondeterministic", "locale"], ["deterministic", "effect", "client boundary"]], ["suppress the warning", "ignore hydration"]),
    ("dependency-advisory", "An advisory lists a vulnerable range, while the lockfile pins one version in that range. What is the evidence-led remediation?", [["lockfile", "pinned version", "installed version"], ["affected range", "advisory", "fixed version"], ["upgrade", "patched version"], ["tests", "verify"]], ["ignore because transitive", "upgrade to latest without compatibility check"]),
    ("readiness-failure", "A rollout stalls because new pods are unready while old pods serve traffic. What evidence and safe action come first?", [["events", "probe", "readiness"], ["logs", "revision", "configuration"], ["rollback", "pause", "documented"], ["verify recovery", "healthy"]], ["delete all pods", "force rollout"]),
    ("tenant-query", "A query is slow only for a tenant with millions of rows. What evidence should precede an index change?", [["query plan", "explain"], ["cardinality", "rows scanned", "parameters"], ["write cost", "storage", "measure"], ["compare", "benchmark"]], ["add every possible index", "rewrite without measurement"]),
    ("kafka-db-order", "A consumer commits an offset before its SQL transaction. What failure window does this create, and what ordering still requires deduplication?", [["loss", "lost update", "failure window"], ["database commit", "durable effect"], ["offset after", "commit offset after"], ["redeliver", "duplicate", "idempotent", "inbox"]], ["atomic across kafka and sql", "exactly once without coordination"]),
    ("parallel-test-collision", "A test flakes only under parallel CI and uses a fixed `/tmp/result.json`. How should the root cause be tested and fixed?", [["shared path", "collision", "overwrite"], ["unique", "per run", "temporary directory"], ["parallel", "concurrent"], ["repeat", "verify"]], ["retry only", "disable all parallel tests"]),
    ("post-idempotency", "A POST request times out after the server may have committed. What API contract makes a client retry safe?", [["idempotency key", "request key"], ["persist", "stored result", "atomic"], ["same body", "different body"], ["retry", "concurrent"]], ["retry always creates", "timeout means failure"]),
    ("canary-config", "A small config diff affects every production replica. How should an agent limit risk and know whether to proceed?", [["blast radius", "rollback"], ["validate", "syntax", "policy"], ["canary", "limited"], ["baseline", "health", "threshold"], ["verify recovery", "stop"]], ["apply cluster-wide immediately", "size of diff proves safe"]),
]


def read_rows(name: str) -> list[dict]:
    return [json.loads(line) for line in (BASE / name).read_text(encoding="utf-8").splitlines() if line.strip()]


def encode(rows: list[dict]) -> bytes:
    return "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows).encode()


def render() -> dict[str, bytes]:
    train, valid, evaluation = (read_rows(name) for name in ("train.jsonl", "valid.jsonl", "eval.jsonl"))
    for index, (topic, prompt, answer) in enumerate(TRAIN, 1):
        train.append({"id": f"problem-solving-v2-{index:02}", "track": "problem-solving", "level": "intermediate",
                      "messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]})
    for index, (prompt, answer) in enumerate(VALID, 1):
        valid.append({"id": f"problem-solving-v2-valid-{index:02}", "track": "problem-solving", "level": "intermediate",
                      "messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]})
    for name, prompt, groups, forbidden in EVAL:
        evaluation.append({"id": f"problem-solving-v2-{name}-heldout", "track": "problem-solving", "level": "intermediate",
                           "prompt": prompt, "must_include_any": groups, "must_not_include": forbidden})
    ids = [row["id"] for rows in (train, valid, evaluation) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate problem-solving dataset IDs")
    train_prompts = {row["messages"][0]["content"] for row in train}
    valid_prompts = {row["messages"][0]["content"] for row in valid}
    eval_prompts = {row["prompt"] for row in evaluation}
    if train_prompts & valid_prompts or train_prompts & eval_prompts or valid_prompts & eval_prompts:
        raise ValueError("problem-solving prompts overlap splits")
    return {"train.jsonl": encode(train), "valid.jsonl": encode(valid), "eval.jsonl": encode(evaluation)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = render()
    if args.check:
        stale = [name for name, data in outputs.items() if not (OUT / name).is_file() or (OUT / name).read_bytes() != data]
        if stale:
            raise SystemExit("Problem-solving v2 dataset is stale: " + ", ".join(stale))
        print("Problem-solving v2 dataset matches its curated source.")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in outputs.items():
        (OUT / name).write_bytes(data)
    print(f"Wrote {len(outputs['train.jsonl'].splitlines())} training, {len(outputs['valid.jsonl'].splitlines())} validation, and {len(outputs['eval.jsonl'].splitlines())} held-out rubric rows.")


if __name__ == "__main__":
    main()
