# Patch repair v3: Go and C# action comparison

## Setup

The v5 problem-solving dataset adds two reviewed repair examples to the previous 190-row training split, producing 192 training rows. The 65 validation and 93 rubric-evaluation rows remain unchanged. Go and C# reference repairs pass the hidden action checks. Fine-tuning used answer-only prompt masking, one trainable layer, batch size 1, 1,024-token sequences, seed 42, and 150 iterations on the Apple M3 with 24 GiB unified memory. Validation loss was 4.970 initially, then 4.821 (25), 3.674 (50), 3.251 (75), 3.414 (100), 3.972 (125), and 3.222 (150). The final checkpoint had training loss 3.489.

## Fresh action-level comparison

| Go/C# held-out repair tasks | Base | v5 adapter, step 150 |
|---|---:|---:|
| Hidden behavior checks | 0/2 | 0/2 |

The evaluator now mirrors Cenere's whitespace-tolerant patch check, so a formatting-only mismatch can proceed to the behavior test. Both Go patches applied after whitespace normalization but still failed to clamp values above 10. The base C# answer contained malformed diff context; the adapter produced a syntactically valid change but retained the original unbounded implementation, so the hidden port-range test still failed. Both versions remain 0/2, and lower validation loss did not produce a measured action-level improvement on these cases.

## Live CLI follow-up

Ran the base model through `cenere code` against a disposable Go fixture without `--apply`. The generated patch passed the whitespace-tolerant applicability check but returned 10 for inputs below 1, which violates the hidden test. The reviewer role incorrectly described that patch as correct. No project files were modified. This confirms that successful patch application and model self-review are not substitutes for running behavior tests.

After bounding planner and reviewer generations, a repeat live run completed without truncating the plan. The 3B model still generated incorrect lower-bound behavior; the reviewer flagged the upper-bound issue but did not identify that values below 1 would also return 10. No patch was applied. The limits reduced role verbosity, but did not make model review reliable.

## Permissioned test-feedback workflow

Added `--check-command` to one-shot coding and coding-terminal sessions. After a separate approval prompt, Cenere copies the project to a disposable workspace, applies the proposed diff there, runs the requested command, and sends failing output back to the coder for one correction round. The original project is not modified by this validation step. The copy excludes `.git`, common generated/dependency directories, and is capped at 1 GiB. This is a temporary working directory, not an OS-level security sandbox.

A live base-model run on the Go clamp task approved `go test .`; the generated patch passed, and the original fixture remained unchanged. A Rust integration test also simulated a bad Python patch, verified the failing assertion output reached the coder, and confirmed its corrected patch passed before review. This validates the feedback plumbing, not general model accuracy. The v5 adapter remains unpromoted because its separate held-out action comparison scored 0/2.

Do not promote `training/adapters/problem-solving-v5`. Keep the base model as the default. These two tasks now count as development evidence rather than a pristine future benchmark. Add broader independently reviewed cases and improve patch generation/tool feedback before treating fine-tuning as an improvement.
