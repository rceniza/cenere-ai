# Cenere multistack v1

This curated seed contains 93 supervised examples (one at each beginner, intermediate, and advanced stage for every catalog track), 31 held-out validation examples (one per track), and 31 rubric evaluation prompts (one per track). The 31 tracks cover broad application areas plus framework families, legacy systems, database engines, mobile/desktop apps, and build toolchains. Examples are concise and are not a substitute for stack-specific code-generation examples and executable tests.

`train.jsonl` and `valid.jsonl` use MLX-LM chat format with `id`, `track`, and `level` metadata. MLX-LM reads `messages` and ignores those extra metadata keys. `eval.jsonl` contains held-out prompts and literal rubric terms; the evaluator reports these heuristic matches, not semantic correctness. Treat the score as a screening signal. Compile generated code, run feature tests, and inspect stack-specific claims before adopting an adapter.

Examples were authored for this repository and are not copied from benchmark test sets. Version-sensitive commands and cloud-provider details are intentionally excluded. Rebuild and validate the committed artifacts with:

```sh
python3 curriculum/datasets/build_multistack_v1.py --check
training/.venv/bin/python -m unittest discover -s training/tests -v
training/.venv/bin/python training/train.py \
  --model training/models/Qwen2.5-Coder-3B-Instruct-4bit \
  --data curriculum/datasets/cenere-multistack-v1 \
  --output training/adapters/cenere-multistack-v1 \
  --iters 10 --num-layers 1
training/.venv/bin/python training/evaluate.py \
  --cases curriculum/datasets/cenere-multistack-v1/eval.jsonl \
  --output training/data/cenere-multistack-v1/base-predictions.jsonl
```

Training is deliberately short and produces only a candidate adapter. Compare base and candidate scores on exactly the same `eval.jsonl`; reject changes that regress any stack materially. The Python MLX training path is for Apple Silicon. No training data includes actual images or video; the multimodal examples test whether the system correctly states that its current text-only model cannot see media.

The first local training and evaluation results are recorded in [`run-2026-10-15.md`](run-2026-10-15.md). That candidate scored lower than the base model's heuristic rubric score and was not promoted.
