# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Cross-database comparison: every database holds the same data as the source.

Three levels, cheapest first: row counts, a checksum of the whole table, and,
when the checksums differ, the exact rows and values that differ.
"""

import pytest

from tests.conftest import TABLES


def differences(source_rows: list[dict], target_rows: list[dict], key: str) -> list[str]:
    """Rows missing, rows extra, and values changed, in words."""
    src = {row[key]: row for row in source_rows}
    tgt = {row[key]: row for row in target_rows}
    found = [f"{key}={k}: missing" for k in src.keys() - tgt.keys()]
    found += [f"{key}={k}: extra" for k in tgt.keys() - src.keys()]
    for k in sorted(src.keys() & tgt.keys(), key=float):
        for col, value in src[k].items():
            if tgt[k].get(col) != value:
                found.append(f"{key}={k} {col}: {value!r} -> {tgt[k].get(col)!r}")
    return found


@pytest.mark.parametrize("table", TABLES)
def test_row_counts_match(source, target, table):
    assert target.count(table) == source.count(table)


@pytest.mark.parametrize("table", TABLES)
def test_same_data_as_the_source(source, target, table):
    key = TABLES[table]
    if target.checksum(table, key) == source.checksum(table, key):
        return  # fast path: the fingerprints match, so every value matches
    diff = differences(source.rows(table, key), target.rows(table, key), key)
    shown = "\n".join(diff[:10])
    pytest.fail(f"{target.name}.{table} differs from {source.name} in {len(diff)} places:\n{shown}")
