# Cenere AI

A local-first coding assistant with a Rust CLI and web app, SQLite memory, sequential coding roles, optional web/browser tools, and an MLX fine-tuning workflow. This Mac has Apple M3 silicon and 24 GB unified memory.

## Run the model

The Python 3.12 environment and a local 3B 4-bit Qwen coder checkpoint are prepared in this checkout. Cenere is the CLI, web app, tool runner, memory store, and training workflow; it does not call Codex or Claude as an agent. The checkpoint is an existing open-weights model, not a model pretrained from scratch. Cenere can run it locally and train small LoRA adapters from reviewed, curated examples. Optional live search uses the internet. See [the model card](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct) for the base model's documented scope and limitations. From the repository root:

```sh
training/.venv/bin/mlx_lm.server \
  --model training/models/Qwen2.5-Coder-3B-Instruct-4bit \
  --host 127.0.0.1 --port 8080
```

To run the Rust app directly in a terminal:

```sh
cargo run -- serve
```

Open <http://127.0.0.1:8787>. The default model endpoint is `http://127.0.0.1:8080/v1/chat/completions`. SQLite is stored at `data/cenere.sqlite3` and can be moved with `CENERE_DATA_DIR`.

## Host the chat UI with Docker

First start the model server on the Mac so the Docker app can reach it:

```sh
training/.venv/bin/mlx_lm.server \
  --model training/models/Qwen2.5-Coder-3B-Instruct-4bit \
  --host 0.0.0.0 --port 8080
```

The model endpoint has no authentication configured. Binding to `0.0.0.0` lets Docker Desktop reach it; restrict access with the macOS firewall.

```sh
docker compose up --build
```

Open <http://127.0.0.1:8787>. Docker runs the Rust web app and persists SQLite data in a volume. The model stays on macOS so MLX can use the M3 GPU; the compose file connects through `host.docker.internal`. The app publishes its web UI on localhost.

## CLI coding assistant

Install the executable so `cenere-ai` opens the interactive menu from any terminal:

```sh
cargo install --path .
cenere-ai
```

With no subcommand, choose coding, chat, or guided study. Coding asks for a workspace and lets you select the source files sent to the model. It offers ask-before-each-action, read-only, or accept-all permissions for the session. Ask mode confirms each shell command, browser request, and patch application. Read-only mode cannot run tools or apply patches. Accept-all skips those prompts for the current process/session and can run arbitrary shell commands or modify the workspace; use it only when you accept that risk.

You can also launch the coding workspace directly:

```sh
cenere-ai terminal --repo /path/to/project --file src/main.rs
```

Enter coding tasks. The planner, coder, and reviewer roles run sequentially through one local model server, using the selected files (up to 48 KB total). The agent can request native OpenAI-compatible `tool_calls` for a shell command, web search, or page inspection; exact legacy XML tool requests remain supported for compatible local models. Ask mode offers one tool at a time and requires confirmation; accept-all is an explicit opt-in. Tool output is passed back as untrusted context. At the prompt, `! cargo check` runs a command after confirmation. For one task, use:

Tool availability does not guarantee the model will choose to call a tool. The current local Qwen 3B model sometimes returns a proposal without using an explicitly requested web tool; use a tool-call-tuned model or verify live information yourself when it skips the request.

```sh
cargo run -- code --repo /path/to/project --file src/main.rs "Add input validation"
```

Add `--apply` to validate the diff and ask before applying it. To start a new app in an empty workspace, omit `--file`; Cenere asks whether to begin with an empty project context and can include multiple new files in its patch. Increase code response length with `CENERE_CODE_MAX_TOKENS` (default 3072; allowed range 256–8192). `--accept-all` can be used for an explicit one-process coding session, for example `cenere-ai --accept-all terminal --repo /path/to/project`; adding `--apply` to `cenere-ai --accept-all code ...` also applies a checked patch without another prompt. Accept-all does not mark its changes as reviewed training examples. The terminal accepts explicit file selection; if none is supplied, it lists source files and asks which ones to include. Browser tools run on the host, not inside the Docker web container. See [CLI design research](docs/cli-research.md) for the open-source comparisons and current permission gaps.

## Step-by-step learning tracks

The CLI and web UI share a staged curriculum covering programming foundations; C, C++, C#, PHP, JavaScript/TypeScript, Node.js, React, Python, Rust, Go/Java; web development; backend/API design; SQL; Git/Linux/shell; Docker; CI/CD; Kubernetes; Kafka/Redpanda; caching; observability/SRE; security; cloud/production; and local AI evaluation. Each track has beginner, intermediate, and advanced stages with practice tasks.

```sh
cargo run -- learn
cargo run -- learn rust
cargo run -- study rust --level beginner --lesson 1
```

Open the web UI and expand **Step-by-step learning tracks**; each task has a **Study** button that asks the local model to explain it, give practice, hints, and a sample solution. The CLI takes a track, stage, and one-based lesson number. This is a guided curriculum, not a claim that every possible question is covered. Use its tasks with the chat or coding terminal and verify outputs with tests and current official documentation. The multimodal track is capability-aware: the current text-only coder model cannot process raw image/video input. That requires a vision-capable model and compatible inference pipeline; video can then be handled through timestamped frames if supported.

## Memory and fine-tuning examples

```sh
cargo run -- remember "This project uses Axum and SQLite."
cargo run -- memories
cargo run -- teach "How should this project validate input?" "Use the shared validator and return a typed error."
cargo run -- export-training
```

The web chat has a correction form and a **Helpful · save reviewed example** action. In the interactive CLI, type `/good` after an answer to approve it as a learning example. In ask mode, a coding patch enters the reviewed-example set only after you approve and apply it. Accept-all can apply code but does not add that code to training. These are human signals, not proof of correctness; run relevant tests before approving coding results. Unreviewed model output is never automatically treated as training truth. Project memory is retrieved from SQLite while answering. CLI and web chat expose read-only web search; the coding CLI additionally offers shell and page-inspection tools behind its permission mode. Only the latest four exchanges are sent as raw chat history. Use `/compact` in CLI or the web **Compact** button to summarize stored turns to SQLite before clearing the raw transcript; the summary and recent turns then provide bounded continuity.

On a configured Apple Silicon host, every eight newly reviewed examples trigger a small background LoRA job automatically; you do not need to run `cenere-ai train`. Training competes with inference for unified memory and may slow responses. Configure the local MLX environment and model as described above. Docker can collect reviewed examples in its SQLite database, but does not train inside the container; export those examples and run training on the configured host. Training creates a candidate adapter and does not switch the live model automatically. Evaluate, fuse, and restart the model server with the adapter before it affects answers. The separate manual command remains available when you want to start a training job explicitly:

```sh
cenere-ai train --iters 30 --num-layers 1
```

SQLite memory can influence answers immediately. Fine-tuning changes weights only when a candidate passes evaluation and is explicitly configured in the model server; Cenere does not hot-swap adapters into a running model process.

The initial Rust sample is in [`curriculum/datasets/rust-foundations-v1`](curriculum/datasets/rust-foundations-v1). The broader curated seed spans 25 tracks and all three curriculum stages in [`curriculum/datasets/cenere-multistack-v1`](curriculum/datasets/cenere-multistack-v1): 75 train, 25 validation, and 25 held-out rubric cases. [`cenere-multistack-v2`](curriculum/datasets/cenere-multistack-v2) adds eight source-linked code answers from locally checked C, C++, PHP, JavaScript, Node, Python, Rust, and Go examples. Build the examples and run the base-model benchmark with:

```sh
python3 curriculum/datasets/build_multistack_v1.py --check
training/.venv/bin/python training/evaluate.py \
  --cases curriculum/datasets/cenere-multistack-v1/eval.jsonl \
  --output training/data/cenere-multistack-v1/base-predictions.jsonl
```

The rubric checks requested terms and forbidden claims. It is a screening signal, not a semantic correctness proof; compile or test code answers in their own stacks. For the v2 code-focused run:

```sh
python3 curriculum/datasets/build_multistack_v2.py --check
training/.venv/bin/python training/train.py \
  --model training/models/Qwen2.5-Coder-3B-Instruct-4bit \
  --data curriculum/datasets/cenere-multistack-v2 \
  --output training/adapters/cenere-multistack-v2 \
  --iters 10 --batch-size 1 --num-layers 1 --max-seq-length 512 --val-batches 2
training/.venv/bin/python training/evaluate.py \
  --cases curriculum/datasets/cenere-multistack-v2/eval.jsonl \
  --output /tmp/cenere-multistack-v2-base.jsonl
```

Run the same evaluation with `--endpoint http://127.0.0.1:8081/v1/chat/completions` against a local candidate server that loads the adapter. See the v2 dataset README for its scope and limitations.

For the Rust reference program and its held-out rubric, run:

```sh
training/.venv/bin/python training/train.py \
  --model training/models/Qwen2.5-Coder-3B-Instruct-4bit \
  --data curriculum/datasets/rust-foundations-v1 \
  --output training/adapters/rust-foundations-v1 --iters 30 --num-layers 1
training/.venv/bin/python training/evaluate.py \
  --cases curriculum/datasets/rust-foundations-v1/eval.jsonl
```

The fine-tune remains an experiment until its held-out score improves and code examples compile. Do not promote an adapter based on training loss alone.

For examples collected by the Docker web app, export from its persistent database and copy the JSONL to the host training directory:

```sh
docker compose exec cenere cenere export-training --output /training-data/train.jsonl
docker compose cp cenere:/training-data/train.jsonl training/data/train.jsonl
```

## Fine-tune an adapter

See [`training/README.md`](training/README.md). Cenere uses Python and MLX to fine-tune a LoRA adapter for the existing model. The background trainer uses the Mac's unified memory and GPU. It adapts the model; it does not train a foundation model from scratch.

The optional Playwright setup and browser commands are in [`browser/README.md`](browser/README.md). Web search retrieves Bing results through Jina Reader. Browser inspection reads a URL, page text, and page errors; browser startup is on demand.

## How Cenere improves

While coding, save durable project facts with `cenere remember`. Save an answer from the interactive chat with `/good`, click the web chat's reviewed-example button, submit a corrected example, or approve and apply a coding patch. Notes affect later prompts immediately. Reviewed examples remain in SQLite and trigger an automatic background fine-tune on the configured host in batches of eight. Every adapter is still a candidate: the currently running model keeps its loaded weights until evaluation and a deliberate server restart. Set `CENERE_AUTO_TRAIN=false` to turn off automatic training while retaining example collection.

## Continuous integration

GitHub Actions checks Rust formatting, runs the Rust and Python training-data tests, and builds the production Docker image on pushes to `main`, pull requests, and manual dispatch.

See [`docs/architecture.md`](docs/architecture.md) for prompt/RAM boundaries, SQLite concurrency limits, and the current training footprint.
