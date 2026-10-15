# Patch repair v1

This small action benchmark asks a model to repair isolated Python and Rust bugs by returning a unified diff. The prompts show only the buggy source file; separate hidden tests exercise boundary behavior. `training/evaluate.py` generates responses and marks these cases as generated-only. `training/evaluate_patch.py` applies each diff in a temporary directory and runs the checked-in validation commands without a shell.

Run it against a local OpenAI-compatible model endpoint:

```sh
training/.venv/bin/python training/evaluate.py \
  --cases curriculum/evaluations/patch-repair-v1/cases.jsonl \
  --endpoint http://127.0.0.1:8080/v1/chat/completions \
  --max-tokens 800 --output /tmp/patch-repair-predictions.jsonl

training/.venv/bin/python training/evaluate_patch.py \
  --cases curriculum/evaluations/patch-repair-v1/cases.jsonl \
  --predictions /tmp/patch-repair-predictions.jsonl
```

This is a diagnostic benchmark, not a broad coding score. Its initial base-model run passed two of four tasks. One Rust answer showed the intended `dedup` call only as unchanged diff context, so the actual patch made no fix; another Python patch retained last-write-wins behavior. The separately stored hidden tests are part of the repository and are not a security boundary against a model with filesystem access. Use fresh tasks for any final candidate comparison.
