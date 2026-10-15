# Cenere problem-solving v2

This set adds twelve evidence-led engineering scenarios covering container networking, duplicate-safe processing, rolling schema changes, memory growth, frontend hydration, dependency advisories, Kubernetes readiness, tenant-skewed queries, Kafka/SQL failure ordering, flaky parallel tests, retry-safe APIs, and canary configuration. Answers model a repeatable process: inspect concrete evidence, state the likely cause and uncertainty, choose a bounded change, then verify behavior.

The generated dataset has 175 training rows, 59 validation rows, and 81 held-out rubric prompts. The v2 addition contributes twelve training scenarios, six validation questions, and twelve fresh evaluations. Prompts are checked for split overlap; the evaluation rubric is a deterministic lexical screen and cannot establish semantic correctness by itself.

Build and verify the committed files:

```sh
python3 curriculum/datasets/build_problem_solving_v2.py
python3 curriculum/datasets/build_problem_solving_v2.py --check
```

Evaluate the base checkpoint before training:

```sh
python training/evaluate.py \
  --cases curriculum/datasets/cenere-problem-solving-v2/eval.jsonl \
  --endpoint http://127.0.0.1:8080/v1/chat/completions \
  --max-tokens 600 --output /tmp/cenere-problem-solving-v2-base.jsonl
```

Train a small local candidate and evaluate it against the same untouched cases:

```sh
python training/train.py \
  --model training/models/Qwen2.5-Coder-3B-Instruct-4bit \
  --data curriculum/datasets/cenere-problem-solving-v2 \
  --output training/adapters/cenere-problem-solving-v2-candidate \
  --iters 150 --batch-size 1 --num-layers 1 --max-seq-length 1024 --val-batches 2
```

The benchmark measures these scenarios only. Keep adapters unpromoted unless they improve fresh held-out problem-solving and relevant executable or repository-state checks without regressing the existing suites.

See the [local training and evaluation report](../../../training/runs/2026-10-15-problem-solving-v2.md) for the base/candidate comparison and limitations.
