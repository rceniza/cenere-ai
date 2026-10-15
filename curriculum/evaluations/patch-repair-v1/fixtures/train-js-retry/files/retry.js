function shouldRetry(status) {
  return status >= 400;
}

module.exports = { shouldRetry };
