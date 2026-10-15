const assert = require("node:assert/strict");
const { isTrustedRedirect } = require("../redirect.js");

for (const url of ["https://trusted.example", "https://trusted.example/path", "https://trusted.example:443/ok"]) {
  assert.equal(isTrustedRedirect(url), true, url);
}
for (const url of ["http://trusted.example", "https://trusted.example:444", "https://trusted.example.attacker.invalid", "https://trusted.example@attacker.invalid", "https://attacker.invalid/?next=https://trusted.example", "not a URL"]) {
  assert.equal(isTrustedRedirect(url), false, url);
}
