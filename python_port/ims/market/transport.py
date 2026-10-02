"""Lossless column-labelled row tables avoid repeating thousands of JSON keys."""


def wire_payload(result: dict) -> dict:
    if not result.get("valid"):
        return result
    sides = {}
    for side, collections in result["sides"].items():
        packed = {}
        for name, rows in collections.items():
            columns = sorted({key for row in rows for key in row})
            # An absent field differs from a meaningful null. Record each row's
            # absent keys for exact reconstruction, with zero overhead on uniform tables.
            table = {"columns": columns, "rows": [[row.get(key) for key in columns] for row in rows]}
            missing = {str(i): [key for key in columns if key not in row] for i, row in enumerate(rows) if set(row) != set(columns)}
            if missing:
                table["missing"] = missing
            packed[name] = table
        sides[side] = packed
    return {**result, "transport": "ims.market-row-table.v1", "sides": sides}


def unpack_rows(table: dict) -> list[dict]:
    return [{key: val for key, val in zip(table["columns"], row) if key not in table.get("missing", {}).get(str(i), [])}
            for i, row in enumerate(table["rows"])]
