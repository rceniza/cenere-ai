# Patch repair v1 baseline

## Evaluation design

The action benchmark contains four isolated buggy fixtures across Python and Rust. The model sees the source and must return a unified diff. The harness applies the patch in a temporary directory and runs hidden behavior tests for boolean parsing, TCP port boundaries, sorting/deduplication, and first-occurrence preservation. The generated-only path in `training/evaluate.py` avoids reporting lexical rubric success for these tasks.

## Base-model result

The verified base checkpoint produced four responses. The lexical prompt rubric marked all four as generated; the action evaluator passed **2/4**. The boolean parser patch passed. The port parser patch passed the checked cases. The Rust answer contained `dedup` as unchanged diff context, so it made no change and failed. The row-deduplication patch retained an unconditional last-write-wins assignment and failed the first-occurrence test.

This is a more direct signal than the earlier phrase-based problem-solving rubric, but four small deterministic tasks cannot establish general code-repair or repository-agent ability. Add reviewed repair examples to training data and keep a new set of behavior tests for the candidate comparison.
