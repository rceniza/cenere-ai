function isTrustedRedirect(raw) {
  return raw.startsWith("https://trusted.example");
}

module.exports = { isTrustedRedirect };
