def parse_retry_after(value):
    if value is None:
        return None
    return int(value)
