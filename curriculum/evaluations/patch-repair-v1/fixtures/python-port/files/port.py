def parse_port(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
