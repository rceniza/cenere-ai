# Problem-solving v1 adapter run

## Dataset and training

This split extends v4 to 163 training rows, 53 validation rows, and 69 total rubric prompts, including ten new problem-solving holdouts. The new practice topics are debugging, test design, performance investigation, concurrency, version-specific research, safe tool use, planning, uncertainty, patch review, algorithm choice, and incident response. The new ten-case eval is diagnostic and lexical; it is not a general reasoning benchmark.

Trained the Qwen2.5-Coder-3B-Instruct-4bit checkpoint with MLX LoRA on an Apple M3 with 24 GiB unified memory: batch 1, one trainable layer (0.013% of parameters), 1,024-token maximum, two validation batches, and 150 iterations. Validation loss went from 5.535 to 1.716. Lower loss did not correspond to strong held-out results.

## Held-out comparison

| Ten new problem-solving prompts | Base | Candidate |
|---|---:|---:|
| Lexical rubric | 1/10 | 2/10 |

The candidate improved only one rubric point and still missed eight cases. It continued to give generic advice, missed version-matched official documentation, and suggested application-level locking or a transaction as a duplicate-prevention guarantee without identifying the database uniqueness constraint. It also sometimes omitted requested diagnostic steps. This is not sufficient evidence of improved problem solving. Keep the adapter unpromoted at `training/adapters/cenere-problem-solving-v1-candidate` and keep the base checkpoint as default.

## Next iteration

Increase the variety and specificity of reviewed examples, especially adversarial concurrency, test-failure diagnosis, evidence-backed research, and tool-feedback loops. Add stronger graders that evaluate the resulting action or code behavior, and keep fresh prompts out of training. For production behavior, the CLI's inspect-edit-run-review loop and tool permissions are part of the problem-solving system; model fine-tuning alone does not provide those capabilities.
