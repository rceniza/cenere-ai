# Cenere multistack v4: verified corrections and executable coding

V4 builds on v3 with ten fact-correction examples based on model errors found in held-out responses, plus a second standard-library coding exercise in eleven language targets. The new corrections cover Fortran array bounds, SQLite WAL writers, Next.js client directives, Tauri filesystem capabilities, ASP.NET Core lifetimes, React request cancellation, Kotlin cancellation, COBOL record layouts, Spring remote transactions, and language/dependency fidelity in generated C.

The generated split contains 151 training rows, 47 validation rows, 59 held-out rubric prompts, and 22 executable coding prompts. The new `sum-int32` task checks valid input, signed 32-bit boundaries, arithmetic overflow, malformed input, extra tokens, exit status, and exact stdout. C# uses the .NET 10 LTS SDK; CI compiles and runs all eleven targets across the same seven cases per task.

Primary documentation used to review the corrections:

- [SQLite WAL concurrency](https://www.sqlite.org/wal.html)
- [Next.js client boundaries](https://nextjs.org/docs/app/api-reference/directives/use-client)
- [Fortran assumed-shape lower bounds](https://www.intel.com/content/www/us/en/docs/fortran-compiler/developer-guide-reference/2023-1/assumed-shape-specifications.html)
- [Tauri filesystem permissions](https://v2.tauri.app/plugin/file-system/)
- [ASP.NET Core dependency lifetimes](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection?view=aspnetcore-10.0)
- [MongoDB transaction scope](https://www.mongodb.com/docs/manual/core/transactions/)
- [.NET 10 support policy](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core)
- [Create a .NET console application](https://learn.microsoft.com/dotnet/core/tutorials/create-console-app/)

Rebuild and verify:

```sh
python3 curriculum/datasets/build_multistack_v4.py --check
python3 -m unittest discover -s training/tests
python3 curriculum/examples/polyglot/check.py --require rust,c,cpp,python,node,typescript,php,go,java
```

Training this set is an experiment, not a promotion. Score both held-out rubric and executable cases against the base model and keep the adapter separate unless measured correctness improves.
