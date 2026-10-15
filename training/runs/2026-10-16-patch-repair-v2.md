# Patch repair v2: local adapter comparison

## Setup

The v4 curriculum adds three verified patch examples to the 187-row advanced problem-solving training split. Training used answer-only prompt masking, one trainable layer, batch size 1, 1,024-token sequences, seed 42, and validation/checkpoint intervals of 25 steps on the Apple M3 with 24 GiB unified memory. Validation loss was 4.970 initially, 4.801 (25), 3.637 (50), 3.231 (75), 3.433 (100), 3.981 (125), and 3.232 (150). Select the step-75 adapter by validation loss; final training loss at step 150 was 3.437.

## Action-level comparison

| Fresh patch-repair v2 tasks | Base | Step-75 candidate |
|---|---:|---:|
| Hidden behavior checks | 2/3 | 0/3 |

The base completed the empty-input average and Rust insertion fixes. It failed exact-origin security validation because it also allowed `https://trusted.example:444`. The candidate failed all three after applying each result: its Python answer was an unusable diff, its URL check compared protocol and hostname but ignored a non-default port, and its Rust patch did not apply because the intended changes appeared as unchanged context. The fixture tests include lookalike hosts, userinfo, non-default ports, duplicate insertion, and empty collections.

Do not promote `training/adapters/cenere-problem-solving-v4-candidate`. Despite lower validation loss, the adapter regressed from the base on these action checks. Keep the base model as default. The adapter output was served from the step-75 checkpoint selected using validation loss, while the base server was verified separately before its run.

These three tasks are now consumed development evidence, not a future unseen final test. Keep adding independently reviewed repair examples and require passing hidden tests across fresh languages and behaviors before promoting any adapter.
