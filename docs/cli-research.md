# CLI design research

Reviewed the public GitHub implementations and docs for Google [Gemini CLI](https://github.com/google-gemini/gemini-cli) and OpenAI [Codex CLI](https://github.com/openai/codex) on 2026-10-15.

Gemini CLI documents a policy engine with `allow`, `deny`, and `ask_user` decisions, rule priorities, approval modes (`default`, `autoEdit`, `plan`, and `yolo`), and an optional sandbox. Its documentation distinguishes read-only planning from normal approval and broad auto-approval. Codex is a Rust terminal coding agent under Apache-2.0; its source and prompt templates are useful references for approval and sandbox design.

Cenere uses its own Rust application, local model endpoint, SQLite data, and browser/shell tools. It does not invoke Codex, Claude, or Gemini as an agent. The current permission modes are:

- **Read-only:** the coding agent cannot call tools or apply patches.
- **Ask:** each shell command, browser action, and patch application needs a confirmation.
- **Accept all:** `cenere-ai --accept-all terminal` or the interactive menu runs requested actions without per-action confirmation for that process/session. A warning is printed. This mode can run destructive shell commands and modify project files; use it only in a workspace you are prepared to restore.

Accept-all grants execution permission, not authority to train on unreviewed output. Automatically applied patches are not saved as training examples in this mode. Examples enter the training set only through a separate review action.

Current limitation: Cenere does not yet have Gemini-style path/command policies, an immutable deny list, or a sandbox around shell tools. The default ask mode remains the recommended mode. Future permission work should add path-scoped rules and an isolated command runner before adding permanent allow rules.

The repositories are design references, not runtime dependencies. Cenere does not copy their agent implementation or pull in their source tree.

For model adaptation, the current [MLX-LM LoRA guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md) documents LoRA and QLoRA, chat-format datasets, and optional validation data. This is a resource-efficient way to adapt an existing compatible checkpoint; it is not pretraining a new foundation model. The [Qwen2.5-Coder model card](https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct) identifies the recommended checkpoint as a text-generation model. Raw image/video analysis would require a vision-capable checkpoint and a compatible serving/input pipeline.

“Search everything on the internet” cannot be exhaustively guaranteed. Cenere should search authoritative, relevant sources when the question is time-sensitive or outside the model's reliable knowledge, return source links, and state what it could not verify. A web search result is context for an answer, not automatic training data; only reviewed and locally validated examples should enter fine-tuning datasets.
