# Cenere problem-solving v5

This split extends problem-solving v4 with two reviewed, executable patch repairs: Go whitespace normalization and C# tag parsing. Both reference changes pass hidden local behavior checks. The v5 training split contains 192 examples; validation (65) and rubric evaluation (93) are copied unchanged from v4 to preserve their separation.

Regenerate with `python3 curriculum/datasets/build_problem_solving_v5.py`; validate with `--check`. These examples are supervised fine-tuning data, not autonomous online learning. Model adapters remain experimental and should be promoted only after held-out behavior checks improve.
