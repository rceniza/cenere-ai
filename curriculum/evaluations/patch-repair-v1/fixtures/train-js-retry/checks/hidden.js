const assert = require("node:assert/strict");
const { shouldRetry } = require("../retry.js");

for (const status of [408, 425, 429, 500, 503, 599]) {
  assert.equal(shouldRetry(status), true, String(status));
}
for (const status of [200, 302, 400, 401, 404, 499, 600]) {
  assert.equal(shouldRetry(status), false, String(status));
}
