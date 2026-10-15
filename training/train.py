#!/usr/bin/env python3
"""Run a deliberately small LoRA fine-tune using Apple's MLX-LM."""

import argparse
import json
import platform
import subprocess
import sys
from pathlib import Path


def validate_dataset(data_dir: Path) -> None:
    train_file = data_dir / "train.jsonl"
    if not train_file.is_file():
        raise SystemExit(f"Missing {train_file}; prepare reviewed chat examples first.")
    count = 0
    with train_file.open(encoding="utf-8") as source:
        for line_no, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise SystemExit(f"Invalid JSON at {train_file}:{line_no}: {error}") from error
            if not isinstance(row, dict):
                raise SystemExit(f"Expected a JSON object at {train_file}:{line_no}.")
            messages = row.get("messages")
            if not isinstance(messages, list) or len(messages) < 2:
                raise SystemExit(f"Expected a chat 'messages' list at {train_file}:{line_no}.")
            if any(not isinstance(message, dict) for message in messages):
                raise SystemExit(f"Each message must be an object at {train_file}:{line_no}.")
            if messages[-1].get("role") != "assistant" or not isinstance(messages[-1].get("content"), str) or not messages[-1].get("content", "").strip():
                raise SystemExit(f"Each example must end with a non-empty assistant answer at line {line_no}.")
            if not any(message.get("role") == "user" and isinstance(message.get("content"), str) and message["content"].strip() for message in messages):
                raise SystemExit(f"Expected at least one user message at line {line_no}.")
            count += 1
    if count < 2:
        raise SystemExit("Use at least two reviewed training examples; a single example is not a useful fine-tune.")
    print(f"Validated {count} training examples.")
    valid = data_dir / "valid.jsonl"
    if valid.exists():
        print("Validation split found.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="MLX model repo or local MLX model path")
    parser.add_argument("--data", type=Path, default=Path("data"), help="Directory containing train.jsonl and optional valid.jsonl")
    parser.add_argument("--output", type=Path, default=Path("adapters/cenere-lora"))
    parser.add_argument("--iters", type=int, default=100, help="Start small; default is a short trial run")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--num-layers", type=int, default=4)
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--val-batches", type=int, default=2)
    args = parser.parse_args()

    if platform.system() != "Darwin" or platform.machine() not in {"arm64", "aarch64"}:
        raise SystemExit("This training entry point targets Apple Silicon and MLX.")
    if args.iters < 1 or args.batch_size < 1 or args.num_layers < 1 or args.max_seq_length < 1 or args.val_batches < 1:
        raise SystemExit("iters, batch-size, num-layers, max-seq-length, and val-batches must be positive.")
    validate_dataset(args.data)
    args.output.mkdir(parents=True, exist_ok=True)

    lora_command = Path(sys.executable).with_name("mlx_lm.lora")
    if not lora_command.is_file():
        raise SystemExit(f"Missing {lora_command}; install requirements in this Python environment.")
    command = [
        str(lora_command), "--model", args.model,
        "--train", "--data", str(args.data), "--adapter-path", str(args.output),
        "--iters", str(args.iters), "--batch-size", str(args.batch_size),
        "--num-layers", str(args.num_layers), "--max-seq-length", str(args.max_seq_length),
        "--val-batches", str(args.val_batches),
    ]
    command.append("--grad-checkpoint")
    print("Starting MLX LoRA training with batch size 1 and a limited layer count.")
    print("Close memory-heavy apps first. Stop with Ctrl-C if macOS memory pressure turns yellow or red.")
    print("Command:", " ".join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
