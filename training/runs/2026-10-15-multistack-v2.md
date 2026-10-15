# 2026-10-15: multistack v2 trial

## Setup

- Base checkpoint: `Qwen2.5-Coder-3B-Instruct-4bit`, local MLX model.
- Dataset: `cenere-multistack-v2`, 83 train rows and 25 validation rows; the held-out set has 25 rubric cases.
- Adapter: 10 QLoRA iterations, batch size 1, one trainable layer, sequence length 512, two validation batches.
- Host: Apple Silicon M3, 24 GB unified memory. The process completed while the base inference server was running; observed system free memory was about 44% during evaluation.

## Results

| Measure | Base | Candidate |
| --- | ---: | ---: |
| Held-out rubric pass | 5/25 (20%) | 4/25 (16%) |
| Validation loss reported during run | — | 4.796 at initial validation, 4.675 at iteration 10 |
| Training loss at iteration 10 | — | 4.524 |

The adapter was not promoted because its held-out score regressed. The rubric is a narrow keyword and forbidden-claim screen, not a semantic correctness test. These numbers do not establish general coding competence or reasoning quality. Predictions were written under `/tmp` and are not part of the repository.

## Scope and next data work

The v2 code answers cover checked examples in C, C++, PHP, JavaScript, Node.js, Python, Rust, and Go. This is a small worked-example seed, not training across every frontend, backend, or DevOps technology. Expand with source-linked examples and stack-specific tests, including TypeScript/React, Java/C#, SQL/API, containers, and CI/CD, before trying a longer run. Keep a fixed held-out set and compare both model output and executable checks. SQLite retrieval can supply reviewed project knowledge without changing weights; adapter updates remain separate candidate artifacts.

This trial uses the `mlx-lm` LoRA/QLoRA workflow documented by [mlx-lm](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md). The data-review and held-out-evaluation gate is also motivated by research on continual fine-tuning and catastrophic forgetting ([LORA: Low-Rank Adaptation](https://arxiv.org/abs/2106.09685), [InsCL: A Data-efficient Continual Learning Paradigm](https://arxiv.org/abs/2403.11435)).
