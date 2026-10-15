# Resource and storage boundaries

Cenere is designed as a local, single-user assistant. SQLite keeps durable notes, reviewed examples, chat turns, and compacted summaries on disk. The model server still loads model weights and the active prompt into memory; writing chat history to SQLite cannot remove that inference requirement.

## What enters the model prompt

- The current user message.
- Up to five matching project notes retrieved from SQLite.
- The latest four raw chat exchanges.
- The most recent compacted conversation summary, when one exists.
- For coding tasks, only explicitly selected files, capped at 48 KB total.
- Web search results only after the model requests the read-only search tool. Coding-session shell and page-inspection tools require per-action confirmation.

Use `/compact` in interactive CLI chat/coding mode or the web **Compact** button to summarize stored turns, save the summary in SQLite, and clear the raw transcript. Compaction calls the local model and needs it to be running. The summary is context, not a verified record; check important decisions against the project files.

## Current SQLite profile

The app uses bundled SQLite, WAL journaling, and one connection protected by a Rust mutex. This keeps deployment simple and works well for a local user with modest traffic. WAL lets readers coexist with a writer, but SQLite still has one writer at a time. The process mutex also serializes database operations within Cenere, so adding many simultaneous web users would not scale linearly.

Memory uses SQLite FTS5 with BM25 ranking and returns at most five notes. This is retrieval-augmented generation (RAG): notes stay on disk, relevant matches are selected for a prompt, and the model answers from that bounded context. It does not update model weights. FTS5 token search is not semantic/vector search; if evaluation finds relevant notes that use different vocabulary, add embeddings and compare retrieval quality before introducing a vector extension. `sqlite-vec` is one Rust-compatible option, but it is pre-v1 and would add build and upgrade risk. If concurrent users become a real requirement, first add load measurements and a connection pool with short transactions; move to a client/server database only when SQLite becomes the measured bottleneck.

## Training footprint

Reviewed examples remain in SQLite until exported for training. The optional Apple Silicon MLX LoRA job uses the model and training data in memory and competes with inference for unified memory. It creates an adapter candidate; the running model does not acquire new weights until the adapter is evaluated and explicitly served. Docker hosts the Rust app and persistent SQLite volume, while MLX training runs on the Apple Silicon host.

## Media capability boundary

The local checkpoint's `config.json` declares `model_type: qwen2` and `architectures: [Qwen2ForCausalLM]`; its directory contains tokenizer files but no image/video processor. The Rust chat request accepts a text string and rejects unknown fields, image/video fields, and multimodal content arrays. Tests cover each rejection. This build can discuss text supplied by a person or OCR step, but it does not inspect raw image or video input.

The official [Qwen2.5-Coder-3B model card](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct) identifies it as text generation. Qwen publishes a separate [Qwen2.5-VL-3B model card](https://huggingface.co/Qwen/Qwen2.5-VL-3B-Instruct) with an image-text processor and examples for timestamped video/frame inputs. That is a possible later model/pipeline, not a capability of Cenere's currently installed checkpoint or Rust endpoint.
