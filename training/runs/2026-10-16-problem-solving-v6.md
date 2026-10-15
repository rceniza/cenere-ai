# Problem-solving v6: test-feedback trial

## Data and setup

Problem-solving v6 extends the reviewed v5 training split from 192 to 196 examples with four test-feedback patch repairs in Python, JavaScript, Rust, and Go. It includes failing test output in each prompt. The 65 validation and 93 rubric evaluation rows were copied unchanged. Reference patches passed their fixture checks. The separate patch-repair-v4 action set contains four fresh cases across Python, Rust, PHP, and Go; none of its prompts or solutions were added to training.

The local Qwen2.5-Coder-3B-Instruct 4-bit MLX model was fine-tuned for 100 iterations on an Apple Silicon machine with 8 CPU cores and 24 GiB unified memory. Training used batch size 1, one trainable layer, prompt masking, gradient checkpointing, a 1,024-token limit, learning rate 1e-5, and seed 42. System-wide free memory remained around 36–44% during the run. Validation loss was 5.156 at the initial checkpoint, 4.801 at step 25, 3.680 at step 50, 3.269 at step 75, and 3.439 at step 100. Training loss ended at 1.499.

## Action results

| Patch-repair-v4 cases | Base | v6 adapter, step 75 |
|---|---:|---:|
| Python retry-after parsing | 0/1 | 0/1 |
| Rust port parsing | 0/1 | 0/1 |
| PHP username validation | 0/1 | 0/1 |
| Go sorted unique merge | 0/1 | 0/1 |
| **Total** | **0/4** | **0/4** |

The four generated candidate answers were byte-for-byte identical to the base outputs. The base produced malformed Python/PHP diffs, invalid Rust syntax, and a Go implementation that returned concatenated inputs without sorting or deduplicating them. The adapter repeated these responses. The reference solutions all pass the hidden behavior checks.

On the four training feedback prompts, both base and adapter passed Python, JavaScript, and Go action checks but failed the Rust overflow patch. Their generated responses were also byte-for-byte identical. This is evidence that the run did not improve these measured behaviors, including on the tiny feedback examples; lower validation loss and training loss are not enough to promote it.

## Decision and limits

Keep the v6 adapter unpromoted and the base checkpoint as default. This four-case holdout is a narrow diagnostic, not a broad programming or reasoning score. The test-feedback data is too small to establish generalization. Expand independently reviewed examples, investigate why the trained adapter did not change greedy outputs, and require fresh executable tasks before another promotion decision.
