# Patch-repair v3: Go and C# action checks

This held-out set checks whether generated unified diffs apply and make the tested behavior correct. It contains a Go retry clamp and a C# TCP port-range validator. Hidden checks are copied into an isolated temporary workspace and are not included in the model prompt.

Run generation with `training/evaluate.py --cases curriculum/evaluations/patch-repair-v3/cases.jsonl --output /tmp/predictions.jsonl`, then run the action checks with `training/evaluate_patch.py --cases curriculum/evaluations/patch-repair-v3/cases.jsonl --predictions /tmp/predictions.jsonl`. The benchmark measures only these two narrow repair cases; it does not establish general coding ability.
