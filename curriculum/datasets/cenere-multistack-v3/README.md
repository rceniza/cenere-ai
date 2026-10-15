# Cenere multistack v3: named ecosystem coverage

V3 extends the broad v2 seed with 26 curated, technology-specific explanations for frameworks and systems grouped in the catalog. Topics cover AngularJS migration, Angular, React, Vue, Svelte, Next.js, Express, FastAPI, Django, Laravel, Spring, ASP.NET Core, COBOL, Fortran, Perl, SQLite, PostgreSQL, MySQL, MongoDB, Swift, Kotlin, Flutter, Tauri, Cargo, Gradle, and Make.

The split contains 129 training rows, 37 validation rows, and 49 held-out rubric prompts. The 18 new evaluation prompts target topics distinct from the new training questions. They are scored separately from the executable code benchmark; the rubric is a regression signal, not proof of broad mastery.

Evaluation cases were reviewed against primary documentation for [SQLite WAL concurrency](https://www.sqlite.org/wal.html), [Next.js client boundaries](https://nextjs.org/docs/app/api-reference/directives/use-client), [Fortran array lower bounds](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2023-1/assumed-shape-specifications.html), [ASP.NET Core service lifetimes](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0), [MongoDB transactions](https://www.mongodb.com/docs/manual/core/transactions/), and [Tauri filesystem permissions](https://v2.tauri.app/plugin/file-system/). Held-out answers exposed concrete errors in several of these areas; the next dataset revision will add correction examples.

Rebuild and check the generated files:

```sh
python3 curriculum/datasets/build_multistack_v3.py --check
```

Run the resource-limited MLX trial from the repository root:

```sh
training/.venv/bin/python training/train.py \
  --model training/models/Qwen2.5-Coder-3B-Instruct-4bit \
  --data curriculum/datasets/cenere-multistack-v3 \
  --output training/adapters/cenere-multistack-v3-candidate \
  --iters 10 --batch-size 1 --num-layers 1 --max-seq-length 512 --val-batches 2
```

Compare the base and adapter on the same 18 new held-out prompts and the complete executable code set before considering promotion. Keep this candidate separate unless it improves the measured behavior without regressions.
