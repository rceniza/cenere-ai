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

The memory lookup is a bounded substring search and then returns at most five notes. It is exact to the stored text match; it is not semantic/vector search and it does not read the entire database into the prompt. As note volume grows, add a measured full-text index and retain a substring fallback for code and punctuation queries. If concurrent users become a real requirement, first add load measurements and a connection pool with short transactions; move to a client/server database only when SQLite becomes the measured bottleneck.

## Training footprint

Reviewed examples remain in SQLite until exported for training. The optional Apple Silicon MLX LoRA job uses the model and training data in memory and competes with inference for unified memory. It creates an adapter candidate; the running model does not acquire new weights until the adapter is evaluated and explicitly served. Docker hosts the Rust app and persistent SQLite volume, while MLX training runs on the Apple Silicon host.
