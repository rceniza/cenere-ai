# Patch repair v3: Go and C# action comparison

## Setup

The v5 problem-solving dataset adds two reviewed repair examples to the previous 190-row training split, producing 192 training rows. The 65 validation and 93 rubric-evaluation rows remain unchanged. Go and C# reference repairs pass the hidden action checks. Fine-tuning used answer-only prompt masking, one trainable layer, batch size 1, 1,024-token sequences, seed 42, and 150 iterations on the Apple M3 with 24 GiB unified memory. Validation loss was 4.970 initially, then 4.821 (25), 3.674 (50), 3.251 (75), 3.414 (100), 3.972 (125), and 3.222 (150). The final checkpoint had training loss 3.489.

## Fresh action-level comparison

| Go/C# held-out repair tasks | Base | v5 adapter, step 150 |
|---|---:|---:|
| Hidden behavior checks | 0/2 | 0/2 |

The evaluator now mirrors Cenere's whitespace-tolerant patch check, so a formatting-only mismatch can proceed to the behavior test. Both Go patches applied after whitespace normalization but still failed to clamp values above 10. The base C# answer contained malformed diff context; the adapter produced a syntactically valid change but retained the original unbounded implementation, so the hidden port-range test still failed. Both versions remain 0/2, and lower validation loss did not produce a measured action-level improvement on these cases.

## Live CLI follow-up

Ran the base model through `cenere code` against a disposable Go fixture without `--apply`. The generated patch passed the whitespace-tolerant applicability check but returned 10 for inputs below 1, which violates the hidden test. The reviewer role incorrectly described that patch as correct. No project files were modified. This confirms that successful patch application and model self-review are not substitutes for running behavior tests; future agent work should add permissioned test execution and send real test failures back to the coder.

Do not promote `training/adapters/problem-solving-v5`. Keep the base model as the default. These two tasks now count as development evidence rather than a pristine future benchmark. Add broader independently reviewed cases and improve patch generation/tool feedback before treating fine-tuning as an improvement.
