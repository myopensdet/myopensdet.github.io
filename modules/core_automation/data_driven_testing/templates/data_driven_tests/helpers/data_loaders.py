# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Load test cases from CSV, JSON, YAML or Excel files, and turn them into pytest cases.

    @pytest.mark.parametrize("row", cases("signup_cases.csv"))
    def test_signup(row): ...

Every row needs a "case" column: it becomes the test's name. A "known_bug" column
with a bug id marks that row as a known failure until the bug is fixed.
"""

import csv
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pytest
import yaml

TEST_DATA = Path(__file__).resolve().parents[1] / "test_data"


def load_rows(file_name: str, sheet: str | None = None) -> list[dict]:
    """Every row of a data file, as a list of dicts. The file type comes from its ending."""
    path = TEST_DATA / file_name
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return _read_csv(path)
    if suffix == ".json":
        return _cases_from(json.loads(path.read_text(encoding="utf-8")), file_name)
    if suffix in (".yaml", ".yml"):
        return _cases_from(yaml.safe_load(path.read_text(encoding="utf-8")), file_name)
    if suffix == ".xlsx":
        return _read_excel(path, sheet)
    raise ValueError(f"{file_name}: can't read {suffix} files")


def _read_csv(path: Path) -> list[dict]:
    # utf-8-sig drops the invisible mark Excel puts at the start of CSV files it saves.
    with path.open(encoding="utf-8-sig", newline="") as file:
        lines = (line for line in file if not line.startswith("#"))  # comment lines
        rows = list(csv.DictReader(lines))
    for number, row in enumerate(rows, start=1):
        if None in row or None in row.values():
            raise ValueError(f"{path.name}, data row {number}: not the same number of columns")
    return rows


def _cases_from(data, file_name: str) -> list[dict]:
    """JSON and YAML files hold a list of cases, or {"cases": [...]} with a comment beside it."""
    rows = data["cases"] if isinstance(data, dict) else data
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        raise ValueError(f"{file_name}: expected a list of cases")
    return rows


def _read_excel(path: Path, sheet: str | None) -> list[dict]:
    from openpyxl import load_workbook  # only needed for Excel files

    # data_only=True gives the value a formula last showed in Excel, not the formula.
    workbook = load_workbook(path, read_only=True, data_only=True)
    try:
        worksheet = workbook[sheet] if sheet else workbook.active
        values = worksheet.iter_rows(values_only=True)
        header = next(values)
        return [
            dict(zip(header, row, strict=True))
            for row in values
            if any(cell is not None for cell in row)  # skip empty rows at the end
        ]
    finally:
        workbook.close()


def cases(file_name: str, sheet: str | None = None, id_field: str = "case") -> list:
    """The rows of a data file as pytest cases, named by id_field."""
    params, seen = [], set()
    for number, row in enumerate(load_rows(file_name, sheet), start=1):
        case_id = row.get(id_field)
        if not case_id:
            raise ValueError(f"{file_name}, case {number}: no '{id_field}' value")
        if case_id in seen:
            raise ValueError(f"{file_name}: two cases are called {case_id!r}")
        seen.add(case_id)
        marks = []
        if row.get("known_bug"):
            reason = f"Known bug {row['known_bug']}"
            marks.append(pytest.mark.xfail(reason=reason, raises=AssertionError, strict=True))
        params.append(pytest.param(row, id=str(case_id), marks=marks))
    return params


# Data files hold text. These turn it into the types the code under test expects.


def to_decimal(value) -> Decimal:
    """Money as an exact Decimal. str() first: Decimal(19.99) is 19.98999999999999843..."""
    try:
        return Decimal(str(value).strip())
    except InvalidOperation:
        raise ValueError(f"Not a number: {value!r}") from None


def to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ("true", "yes", "1"):
        return True
    if text in ("false", "no", "0", ""):
        return False
    raise ValueError(f"Not true or false: {value!r}")


def to_int(value) -> int:
    return int(str(value).strip())
