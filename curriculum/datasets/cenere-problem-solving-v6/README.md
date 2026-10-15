# Cenere problem-solving v6

This version extends the 192-row v5 training split with four supervised examples that include failed test output and a corrected patch. The additions cover Python, JavaScript, Rust, and Go. Validation and rubric evaluation rows are copied unchanged from v5.

The separate four-case executable holdout is patch-repair-v4. Its prompts and reference answers are not copied into this training dataset. The benchmark is diagnostic and does not measure general reasoning ability.

Regenerate from the curated source with python3 curriculum/datasets/build_problem_solving_v6.py; check reproducibility with --check. The examples are reviewed supervision, not autonomous online learning.
