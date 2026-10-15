# Local LoRA fine-tuning on Apple silicon

This is an optional Python component for adapting an existing MLX-compatible model. It produces a LoRA adapter; it does not train a foundation model from scratch. Training examples are kept outside Git under `training/data/`.

## Setup

From the repository root:

```sh
cd training
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
mkdir -p data
```

Create `training/data/train.jsonl` with one reviewed example per line, or from the repository root save corrected examples with `cargo run -- teach ...` and export them with `cargo run -- export-training`. MLX-LM chat format:

```json
{"messages":[{"role":"user","content":"Ask a coding task"},{"role":"assistant","content":"A correct answer or patch"}]}
```

Use examples that represent the behavior you want. Keep a separate `valid.jsonl` for examples excluded from training so you can check whether the adapter generalizes. Do not train on unreviewed assistant output as if it were ground truth.

## First small run

```sh
python train.py --model models/Qwen2.5-Coder-3B-Instruct-4bit --data data \
  --iters 10 --batch-size 1 --num-layers 1 --max-seq-length 512 --val-batches 2
```

The suggested starter is a 3B 4-bit MLX coding model; its local files are about 1.6 GB. The conservative example uses batch size 1, one trainable layer, a 512-token sequence limit, two validation batches, and a short run. Model choice, prompt length, dataset size, and thermal conditions still affect peak memory. Watch Activity Monitor's Memory Pressure and stop if it turns yellow/red or the machine begins heavy swapping. Adapter weights are saved under `training/adapters/` and excluded from Git. See the [model card](https://huggingface.co/mlx-community/Qwen2.5-Coder-3B-Instruct-4bit) for model format and license.

The `mlx-lm` project supports LoRA/QLoRA, validation data, and low-memory adjustments such as smaller batches or fewer layers. See its [fine-tuning guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md) before changing training options.

The MLX server can serve an adapter at startup, without fusing another model copy. Stop the existing server before using the same port, or use a second port for a side-by-side evaluation:

```sh
mlx_lm.server --model models/Qwen2.5-Coder-3B-Instruct-4bit \
  --adapter-path adapters/cenere-lora --host 127.0.0.1 --port 8081
```

The server exposes the OpenAI-compatible endpoint expected by Cenere. This loads the adapter when the process starts; it does not hot-swap weights into an already running server. Fusion remains an option when a standalone model artifact is useful, and those model files are excluded from Git. See [`../curriculum/datasets/cenere-multistack-v1`](../curriculum/datasets/cenere-multistack-v1) for the 25-track training/evaluation seed and the [2026-10-15 run report](../curriculum/datasets/cenere-multistack-v1/run-2026-10-15.md).
