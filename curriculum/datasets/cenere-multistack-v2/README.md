# Cenere multistack v2: checked code answers

This dataset adds eight complete supervised code answers to the v1 curriculum seed: C, C++, PHP, JavaScript, Node.js, Python, Rust, and Go. Each answer is read directly from the repository's polyglot reference implementation. The polyglot harness compiles/runs the implementations against seven shared input/output cases; Java is not included because this host does not have a working runtime. Java, C#, React, and the DevOps tracks are not represented by code answers in this batch.

The split is 83 training rows (75 v1 curriculum explanations plus eight code answers), 25 validation rows, and the same 25 held-out rubric prompts as v1. None of the new training questions appears in validation or evaluation. The shared task is deliberately small; it measures and teaches a narrow coding pattern, not broad language competence.

Rebuild and validate the generated files:

```sh
python3 curriculum/datasets/build_multistack_v2.py --check
python3 curriculum/examples/polyglot/check.py
```

The adapter run should be short and resource-aware. Compare base and candidate on the exact same `eval.jsonl`, inspect the generated answers, and do not promote an adapter that regresses. A lower training or validation loss alone does not demonstrate better answers.
