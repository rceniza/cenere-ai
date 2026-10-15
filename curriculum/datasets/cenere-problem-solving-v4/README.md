# Cenere problem-solving v4

V4 builds on the advanced problem-solving set and adds three reviewed patch-repair examples in Python, JavaScript, and Rust. Each generated answer is a unified diff; its source fixture is checked by the same isolated test harness used for action evaluation. The dataset contains 190 training rows, 65 validation rows, and 93 rubric cases.

Rebuild and verify the data:

```sh
python3 curriculum/datasets/build_problem_solving_v4.py
python3 curriculum/datasets/build_problem_solving_v4.py --check
```

Train an answer-masked LoRA candidate:

```sh
training/.venv/bin/python training/train.py \
  --model training/models/Qwen2.5-Coder-3B-Instruct-4bit \
  --data curriculum/datasets/cenere-problem-solving-v4 \
  --output training/adapters/cenere-problem-solving-v4-candidate \
  --iters 150 --batch-size 1 --num-layers 1 --max-seq-length 1024 \
  --val-batches 2 --steps-per-eval 25 --save-every 25
```

Compare code-repair behavior on the separate [`patch-repair-v2`](../../evaluations/patch-repair-v2/README.md) fixtures. Do not use the training fixes or the already-used v1 action set as an unseen final test.
