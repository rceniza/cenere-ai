import sys

parts = sys.stdin.read().split()
if len(parts) != 2:
    raise SystemExit(2)
try:
    values = [int(part, 10) for part in parts]
except ValueError:
    raise SystemExit(2)
if any(value < -2147483648 or value > 2147483647 for value in values):
    raise SystemExit(2)
total = values[0] + values[1]
if total < -2147483648 or total > 2147483647:
    raise SystemExit(2)
print(total)
