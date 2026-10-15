import sys


def normalize(line: str) -> list[int]:
    if not line.strip():
        return []
    values = []
    for token in line.split(","):
        value = int(token.strip())
        if not -(2**31) <= value < 2**31:
            raise ValueError("outside signed 32-bit range")
        values.append(value)
    return sorted(set(values))


try:
    print("[" + ",".join(map(str, normalize(sys.stdin.readline()))) + "]")
except ValueError:
    raise SystemExit(2)
