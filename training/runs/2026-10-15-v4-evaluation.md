# V4 curriculum and adapter evaluation

## Training

V4 contains 151 training rows, 47 validation rows, 59 rubric evaluation prompts, and 22 executable coding prompts. The signed 32-bit sum task asks for a standalone program in eleven language targets, including C#/.NET 10; the normalizer task adds a second C# executable example. The checked-in reference programs pass seven input cases per task.

Trained Qwen2.5-Coder-3B-Instruct-4bit with MLX LoRA on an Apple M3 with 24 GiB unified memory. The run used batch size 1, one trainable layer (0.013% of parameters), sequence limit 1024, two validation batches, and 150 iterations. Initial validation loss was 5.616; final validation loss was 2.018 and final training loss was 2.325. No examples were truncated at this sequence limit.

## Held-out results

| Evaluation | Base | V4 candidate |
|---|---:|---:|
| New technical correction prompts, lexical rubric | 4/10 | 3/10 |
| Sum task, response-format/keyword rubric | 6/10 | 10/10 |
| Sum task, compile and seven executable cases per language | 0/10 | 0/10 |

The candidate learned to satisfy the lightweight response rubric but did not produce a single fully executable solution. It failed on compiler errors, input parsing, overflow and exact-output behavior. The base/candidate comparison shows why matching rubric terms cannot stand in for functional correctness. Neither this candidate nor the base meets the 10/10 executable target, and the candidate also regresses on this small correction set. Do not promote it.

## Evaluation policy

Keep training, validation, and final test prompts disjoint. Do not move a held-out prompt or its answer into training and then continue reporting that same prompt as an unseen result. Use reviewed examples from failures for the next training iteration, and measure that iteration on a newly authored or newly released holdout. This follows the separation guidance in the [fine-tuning best practices](https://developers.openai.com/api/docs/guides/fine-tuning-best-practices). Report the exact task scope, per-case results, toolchains, and evaluator limitations. For code generation, require compilation and behavior tests; a lexical or model-graded score is diagnostic only. This aligns with execution-based code benchmarks such as [LiveCodeBench](https://github.com/livecodebench/livecodebench), which also evaluates code execution and self-repair. Fixed small sets can measure this task suite, not general competence across every framework or real repository task; realistic repository-level agent tasks need a separate benchmark such as [SWE-bench Verified](https://openai.com/index/introducing-swe-bench-verified/), with careful attention to test quality and contamination.

## Outcome

Keep the adapter as an unpromoted experiment at `training/adapters/cenere-multistack-v4-candidate`. Restore the base model as the default. Continue by improving reviewed code examples and using compiler/runtime feedback as training signals, while holding out a fresh executable test set for each comparison.

## C# follow-up

Added C# reference implementations for both executable tasks and built them with .NET SDK 10.0.402. On separately worded held-out prompts, the base checkpoint scored 0/2 on compile-and-run evaluation. A second 150-iteration, one-layer LoRA candidate trained on the expanded 151-row dataset also scored 0/2; it passed the simple fence/keyword rubric 2/2 while failing executable behavior. The normalizer response repeated using directives instead of providing a complete program, and the sum response accepted 32-bit overflow and failed required rejection cases. Keep `training/adapters/cenere-multistack-v4-csharp-both-candidate` unpromoted. This confirms that lexical checks and lower training loss cannot stand in for execution-based problem solving. The C# heldout cases are small diagnostic examples, not a broad C# competence score.
