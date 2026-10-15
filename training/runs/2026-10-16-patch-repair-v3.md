# Patch repair v3: Go and C# action comparison

## Setup

The v5 problem-solving dataset adds two reviewed repair examples to the previous 190-row training split, producing 192 training rows. The 65 validation and 93 rubric-evaluation rows remain unchanged. Go and C# reference repairs pass the hidden action checks. Fine-tuning used answer-only prompt masking, one trainable layer, batch size 1, 1,024-token sequences, seed 42, and 150 iterations on the Apple M3 with 24 GiB unified memory. Validation loss was 4.970 initially, then 4.821 (25), 3.674 (50), 3.251 (75), 3.414 (100), 3.972 (125), and 3.222 (150). The final checkpoint had training loss 3.489.

## Fresh action-level comparison

| Go/C# held-out repair tasks | Base | v5 adapter, step 150 |
|---|---:|---:|
| Hidden behavior checks | 0/2 | 0/2 |

The Go answer from both models repeated a hunk without changing the behavior and the patch did not apply. The base C# answer contained malformed diff context; the adapter produced a syntactically valid change but retained the original unbounded implementation, so the hidden port-range test still failed. The result shows that lower validation loss did not produce a measured action-level improvement on these cases.

Do not promote `training/adapters/problem-solving-v5`. Keep the base model as the default. These two tasks now count as development evidence rather than a pristine future benchmark. Add broader independently reviewed cases and improve patch generation/tool feedback before treating fine-tuning as an improvement.
