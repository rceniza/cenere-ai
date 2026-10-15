async function main(): Promise<void> {
  let input = "";
  process.stdin.setEncoding("utf8");
  for await (const chunk of process.stdin) {
    input += chunk as string;
  }

  const line = input.split(/\r?\n/, 1)[0] ?? "";
  const values: number[] = [];
  if (line.trim() !== "") {
    for (const token of line.split(",")) {
      const valueText = token.trim();
      if (!/^[+-]?\d+$/.test(valueText)) {
        process.exitCode = 2;
        return;
      }
      const value = Number(valueText);
      if (!Number.isSafeInteger(value) || value < -2147483648 || value > 2147483647) {
        process.exitCode = 2;
        return;
      }
      values.push(value);
    }
  }

  process.stdout.write(`${JSON.stringify([...new Set(values)].sort((a, b) => a - b))}\n`);
}

void main();
