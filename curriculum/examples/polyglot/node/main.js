const readline = require('node:readline');

const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
rl.once('line', (line) => {
  try {
    const values = line.trim() === '' ? [] : line.split(',').map((part) => {
      const token = part.trim();
      if (!/^[+-]?\d+$/.test(token)) throw new Error('invalid integer');
      const value = Number(token);
      if (!Number.isSafeInteger(value) || value < -2147483648 || value > 2147483647) throw new Error('out of range');
      return value;
    });
    console.log(JSON.stringify([...new Set(values)].sort((a, b) => a - b)));
  } catch {
    process.exitCode = 2;
  }
  rl.close();
});
