# Cenere problem-solving v3

This set adds advanced scenarios involving CI database parity, least-privilege access, responsive browser testing, tool-result validation, untrusted issue content, MCP schemas, conflicting agent edits, shared Git history, secret rotation, Terraform replacements, Kubernetes OOMs, and Kafka lag.

The generated data contains 187 training rows, 65 validation rows, and 93 held-out rubric prompts. The v3 addition contributes twelve advanced worked examples, six validation examples, and twelve new evaluation prompts. Dataset generation checks for duplicate IDs and prompt overlap across splits. The rubric is deterministic and lexical, so it is a screening signal rather than proof of semantic correctness.

Build and verify the committed dataset:

```sh
python3 curriculum/datasets/build_problem_solving_v3.py
python3 curriculum/datasets/build_problem_solving_v3.py --check
```

Train with answer-only loss and frequent validation/checkpoint saves:

```sh
python training/train.py \
  --model training/models/Qwen2.5-Coder-3B-Instruct-4bit \
  --data curriculum/datasets/cenere-problem-solving-v3 \
  --output training/adapters/cenere-problem-solving-v3-candidate \
  --iters 150 --batch-size 1 --num-layers 1 --max-seq-length 1024 \
  --val-batches 2 --steps-per-eval 25 --save-every 25
```

Prompt masking is enabled by default: the adapter loss is applied to assistant answers instead of spending training tokens predicting the user and system prompts. Check validation loss across saved checkpoints, then compare against a fresh held-out set. The v2 prompts are now development evidence and must not be presented as a new unseen test after using them to guide trainer changes.

See the [problem-solving v2 run report](../../../training/runs/2026-10-15-problem-solving-v2.md) for why answer-only loss and tighter checkpoint observation were added.
