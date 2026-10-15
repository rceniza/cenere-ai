def parse_retry_after(value):
    if not isinstance(value, str):
        return None
    text = value.strip(" \t\r\n")
    if not text or any(character < "0" or character > "9" for character in text):
        return None
    seconds = int(text)
    return seconds if seconds <= 86400 else None
