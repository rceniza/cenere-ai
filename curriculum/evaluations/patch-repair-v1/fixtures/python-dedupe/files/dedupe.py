def first_by_id(rows):
    result = {}
    for row in rows:
        result[row["id"]] = row
    return list(result.values())
