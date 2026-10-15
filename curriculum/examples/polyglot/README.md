# Polyglot coding exercise: normalize integer lists

Each program reads one comma-separated line of signed decimal integers from standard input. It prints a JSON array containing the sorted, deduplicated integers. Empty input prints `[]`; malformed tokens and values outside the signed 32-bit range are rejected with a non-zero exit status and no standard output.

The shared cases include whitespace, duplicates, negatives, empty input, malformed input, and range overflow. Run the available implementations with:

```sh
python3 curriculum/examples/polyglot/check.py
```

The checker compiles native examples into a temporary directory, runs every implementation whose compiler/runtime is installed, and reports unavailable toolchains as skips. For a strict local matrix, pass `--require rust,c,cpp,python,node,php,go,java`. Add the required toolchain before using strict mode on another host. This is a small behavioral exercise, not evidence of broad language mastery.
