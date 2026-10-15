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
python train.py --model models/Qwen2.5-Coder-3B-Instruct-4bit --data data --iters 100
```

The suggested starter is a 3B 4-bit MLX coding model; its published model files are about 1.8 GB. Defaults use batch size 1, four trainable layers, and gradient checkpointing to conserve memory. Model choice, sequence length, dataset size, and thermal conditions still affect peak memory. Begin with a short run and watch Activity Monitor's Memory Pressure. Adapter weights are saved under `training/adapters/` and excluded from Git. See the [model card](https://huggingface.co/mlx-community/Qwen2.5-Coder-3B-Instruct-4bit) for model format and license.

The `mlx-lm` project supports LoRA/QLoRA, validation data, and low-memory adjustments such as smaller batches or fewer layers. See its [fine-tuning guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md) before changing training options.

After training, fuse the adapter before serving it to the Rust app:

```sh
mlx_lm.fuse --model models/Qwen2.5-Coder-3B-Instruct-4bit \
  --adapter-path adapters/cenere-lora --save-path models/cenere-fused
mlx_lm.server --model models/cenere-fused --host 127.0.0.1 --port 8080
```

The server exposes the OpenAI-compatible endpoint expected by Cenere. Fused model files are local artifacts and are excluded from Git.
