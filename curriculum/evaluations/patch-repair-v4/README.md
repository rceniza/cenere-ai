# Patch-repair v4: boundary and collection behavior

This fresh action set checks four isolated repairs across Python, Rust, PHP, and Go. Hidden tests cover input boundaries, malformed values, overflow, Unicode policy, duplicate handling, and input mutation. Only the source files listed in each case are shown to the model; hidden checks are copied into an isolated temporary workspace.

Run generation with training/evaluate.py --cases curriculum/evaluations/patch-repair-v4/cases.jsonl --output /tmp/patch-v4-predictions.jsonl, then execute the action checks with training/evaluate_patch.py --cases curriculum/evaluations/patch-repair-v4/cases.jsonl --predictions /tmp/patch-v4-predictions.jsonl.

This four-case diagnostic measures only these behaviors. It is not a general reasoning, language-competence, or repository-agent score. Keep it held out from training for the v6 comparison.
