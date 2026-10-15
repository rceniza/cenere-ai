# 2026-10-15: multistack v2 trial

## Setup

- Base checkpoint: `Qwen2.5-Coder-3B-Instruct-4bit`, local MLX model.
- Dataset: `cenere-multistack-v2`, 83 train rows and 25 validation rows; the held-out set has 25 rubric cases.
- Adapter: 10 QLoRA iterations, batch size 1, one trainable layer, sequence length 512, two validation batches.
- Host: Apple Silicon M3, 24 GB unified memory. The process completed while the base inference server was running; observed system free memory was about 44% during evaluation.

## Results

| Measure | Base | Candidate |
| --- | ---: | ---: |
| Broad held-out rubric pass | 5/25 (20%) | 4/25 (16%) for the 10-iteration adapter |
| Executable code benchmark | 0/8 | 0/8 for 10-iteration, 100-iteration, and 100-iteration/8-layer adapters |
| Validation loss | — | 4.796 initially; 4.675 at 10 iterations; 2.678 at 100 iterations/1 layer; 2.319 at 100 iterations/8 layers |
| Training loss | — | 4.524 at 10 iterations; 2.318 at 100 iterations/1 layer; 1.824 at 100 iterations/8 layers |

The adapters were not promoted because the 10-iteration candidate regressed on the broad held-out score and none of the candidates passed an executable code case, even after 100 iterations and eight trainable layers. The source reference implementations passed all eight executable cases. The rubric is a narrow keyword and forbidden-claim screen, not a semantic correctness test. Training loss fell substantially without yielding correct generated programs; this trial is direct evidence that loss alone is not a good promotion signal. Predictions were written under `/tmp` and are not part of the repository.

## Scope and next data work

The v2 code answers cover checked examples in C, C++, PHP, JavaScript, Node.js, Python, Rust, and Go. This is a small worked-example seed, not training across every frontend, backend, or DevOps technology. The code benchmark uses separate prompts, checks the answer's fence language, compiles where appropriate, and runs seven input/output cases. Expand with source-linked examples and stack-specific tests, including TypeScript/React, Java/C#, SQL/API, containers, and CI/CD, before trying a longer run. SQLite retrieval can supply reviewed project knowledge without changing weights; adapter updates remain separate candidate artifacts.

This trial uses the `mlx-lm` LoRA/QLoRA workflow documented by [mlx-lm](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md). The data-review and held-out-evaluation gate is also motivated by research on continual fine-tuning and catastrophic forgetting ([LORA: Low-Rank Adaptation](https://arxiv.org/abs/2106.09685), [InsCL: A Data-efficient Continual Learning Paradigm](https://arxiv.org/abs/2403.11435)).
