# V3 ecosystem curriculum and adapter run

## Dataset

- 31 catalog tracks and 287 sequenced lessons.
- V3 totals: 129 training rows, 37 validation rows, 49 rubric-held-out prompts.
- Ten checked code examples cover C, C++, PHP, JavaScript, TypeScript, Node.js, Python, Rust, Go, and Java.
- Added 26 framework/system specific training explanations and 18 disjoint held-out prompts.
- All data builders reproduce committed data; 20 Python dataset/training tests pass. The polyglot reference harness passed seven cases for all nine locally required languages after prepending the installed Homebrew JDK to `PATH`.

## Resource-limited training

On an Apple M3 with 24 GiB unified memory, trained Qwen2.5-Coder-3B-Instruct-4bit with MLX LoRA, batch size 1, one trainable layer (0.013% of parameters), sequence limit 512, two validation batches, and ten iterations. The system reported 65% free memory after stopping the local inference server and Android emulator; the Docker web app stayed running.

The initial validation loss was 5.118 and the final observed validation loss was 4.707; final training loss was 4.597. A second isolated run used 100 iterations with the same batch, layer, and sequence limits. Its final validation loss was 2.118 and final training loss was 2.740; one 530-token sequence was truncated by the 512-token maximum. The lower loss still did not demonstrate improved held-out behavior.

## Held-out comparisons

The first 18-case keyword rubric was too literal, so I revised its accepted terms after reviewing raw answers and rescored those exact saved predictions. The corrected lexical rubric scored the base at 8/18, the ten-iteration adapter at 7/18, and the 100-iteration adapter at 6/18. This still is not semantic grading, but it checks meaningful technical requirements and explicit false claims. Manual review found hallucinations the earlier rubric did not catch: Fortran described as zero-based; SQLite WAL described as permitting unlimited concurrent writers; Next.js advised a nonexistent `useClient` hook; and Tauri advised a nonexistent `window.tract` API. Neither adapter should be promoted.

Compared generated code against all ten languages in the held-out executable task set. The base and both candidates scored 0/10, despite all ten responses passing the lightweight fenced-code rubric. Common failures included shell or another language in place of the requested language, undeclared third-party dependencies, extra stdout, incorrect malformed-input handling, and compile errors. This confirms the rubric score is insufficient and that executable checks are necessary.

## Outcome

Keep both adapters as unpromoted experiments under ignored `training/adapters/cenere-multistack-v3-candidate` and `training/adapters/cenere-multistack-v3-100iter-candidate` paths. Do not replace the default model. The next useful work is stronger task-specific coding data, more robust correctness evaluators, and a measured training schedule that demonstrably improves held-out behavior. The default Qwen2.5 Coder checkpoint remains text-only; Cenere's current chat API accepts text and rejects image or video payloads.
