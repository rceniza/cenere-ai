import { readFileSync } from 'node:fs';

const line = readFileSync(0, 'utf8').trim();
const parts = line ? line.split(/\s+/) : [];
if (parts.length !== 2 || parts.some((part) => !/^[+-]?\d+$/.test(part))) process.exit(2);
const values = parts.map(Number);
if (values.some((value) => !Number.isSafeInteger(value) || value < -2147483648 || value > 2147483647)) process.exit(2);
const sum = values[0] + values[1];
if (sum < -2147483648 || sum > 2147483647) process.exit(2);
process.stdout.write(`${sum}\n`);
