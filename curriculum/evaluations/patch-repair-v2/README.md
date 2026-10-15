# Patch repair v2

This fresh action set evaluates Python empty-input averages, JavaScript URL-origin validation, and Rust sorted-unique insertion. The model receives only each buggy source file. The evaluator applies generated diffs in temporary directories and runs hidden behavior tests, including an HTTPS lookalike-host rejection and duplicate/empty collection cases.

Generate and execute candidate patches:

```sh
training/.venv/bin/python training/evaluate.py \
  --cases curriculum/evaluations/patch-repair-v2/cases.jsonl \
  --endpoint http://127.0.0.1:8080/v1/chat/completions \
  --max-tokens 800 --output /tmp/patch-repair-v2-predictions.jsonl

training/.venv/bin/python training/evaluate_patch.py \
  --cases curriculum/evaluations/patch-repair-v2/cases.jsonl \
  --predictions /tmp/patch-repair-v2-predictions.jsonl
```

Keep these cases disjoint from the patch-repair v1 fixtures and the v4 training examples. The set has only three cases and is a diagnostic comparison, not a general code-agent benchmark.
