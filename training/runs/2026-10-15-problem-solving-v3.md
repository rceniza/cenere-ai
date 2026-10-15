# Problem-solving v3: answer-only training experiment

## Dataset and method

V3 contains 187 training rows, 65 validation rows, and 93 rubric cases. The added material covers production database parity, least-privilege access, browser-responsive testing, tool-result/schema validation, untrusted issue content, MCP responses, concurrent agent edits, shared Git recovery, secret rotation, Terraform replacement plans, Kubernetes OOMs, and Kafka consumer lag. Twelve separately authored advanced prompts formed this run's fresh evaluation set.

The training harness now masks system and user prompt tokens by default and saves/validates every 25 iterations. This is meant to focus the loss on assistant responses and make overfitting visible sooner. The 150-iteration MLX LoRA run used batch size 1, one trainable layer (0.013%), sequence length 1,024, two validation batches, learning rate 1e-5, and seed 42 on an Apple M3 with 24 GiB unified memory. Validation losses were 4.023 initially, then 3.369 (25), 3.586 (50), 3.456 (75), 3.403 (100), 3.029 (125), and 3.643 (150); final training loss was 3.411. The step-125 checkpoint was selected using validation loss only.

## Fresh held-out comparison

| Twelve advanced scenarios | Base | Step-125 candidate |
|---|---:|---:|
| Deterministic multi-part rubric | 0/12 | 0/12 |

The base checkpoint was verified from the server process and `/v1/models` before generating its answers. The candidate was served from the saved step-125 adapter checkpoint. Both sets missed required evidence/action/verification details. The candidate sometimes gave a shorter response, but it also proposed retrying with the same credentials instead of diagnosing authorization, and it suggested uploading secrets to a trusted vault rather than refusing exfiltration and rotating the exposed key. Some answers repeated generic checklist items until the token limit. Neither result is acceptable for promotion; keep `training/adapters/cenere-problem-solving-v3-candidate` unpromoted and retain the base model as default.

## Scoring limits and next work

The scorer now ignores a forbidden phrase when the same sentence clearly rejects it, fixing false positives such as “do not use administrator credentials.” It remains a lexical screen, and its all-fail result cannot distinguish an incomplete but safe answer from a technically wrong one unless a forbidden claim or action-level check is included. These twelve prompts are consumed development evidence, not a fresh test for future candidates.

The low validation loss at step 125 did not correspond to a passing held-out result. Before another fine-tune, improve the task grader with human-reviewed decision/action checks and build executable or state-transition tasks where possible. Expand tool-use examples without training hidden chain-of-thought; train concise observable evidence, safe action, and verification summaries. Keep a newly authored holdout for the next comparison.
