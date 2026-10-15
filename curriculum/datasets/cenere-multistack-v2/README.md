# Cenere multistack v2: checked code answers

This dataset adds nine complete supervised code answers to the v1 curriculum seed: C, C++, PHP, JavaScript, TypeScript, Node.js, Python, Rust, and Go. Each answer is read directly from a repository polyglot reference implementation. The harness compiles or runs each available implementation against seven shared input/output cases. Java is skipped on this Mac because its launcher/runtime is unavailable. C#, React, and infrastructure tracks still need stack-specific code tasks in later batches.

The split is 84 training rows (75 v1 curriculum explanations plus nine code answers), 25 validation rows, 25 broad held-out rubric prompts, and nine held-out code prompts. They do not repeat training prompts and are scored by compiling/running generated programs against the shared seven-case behavior suite. Keep the broad rubric and code benchmark as separate signals: the former checks curriculum regression; the latter checks the narrow coding behavior directly.

Rebuild and validate the generated files:

```sh
python3 curriculum/datasets/build_multistack_v2.py --check
python3 curriculum/examples/polyglot/check.py --require rust,c,cpp,python,node,typescript
```

After running `training/evaluate.py` against `code-eval.jsonl`, execute its captured answers with:

```sh
training/.venv/bin/python training/evaluate_code.py \
  --cases curriculum/datasets/cenere-multistack-v2/code-eval.jsonl \
  --predictions /tmp/cenere-multistack-v2-code-predictions.jsonl
```

The adapter run should be short and resource-aware. Compare base and candidate on the exact same `eval.jsonl`, inspect the generated answers, and do not promote an adapter that regresses. A lower training or validation loss alone does not demonstrate better answers.
