# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""CSV import: good files go in whole; bad files are refused whole, with the row number."""

import uuid

from tests.conftest import IMPORT_PATH, count_rows, csv_file, upload

HEADER = "email,name"  # CHANGE: your columns


def unique_email() -> str:
    return f"import-{uuid.uuid4().hex[:8]}@example.com"  # new every run, so reruns work


def test_good_file_imports_every_row():
    before = count_rows()
    data = csv_file(HEADER, f"{unique_email()},Arshad Test", f"{unique_email()},Mia Khan")
    answer = upload(IMPORT_PATH, "customers.csv", data, "text/csv")
    assert answer.status_code in (200, 201), answer.text
    assert answer.json()["imported"] == 2
    assert count_rows() == before + 2


def test_excel_style_file_with_bom_and_accents_imports():
    """Excel saves "CSV UTF-8" with a hidden BOM at the start. Names have accents."""
    data = csv_file(HEADER, f"{unique_email()},Zoë Ångström", bom=True)
    answer = upload(IMPORT_PATH, "from-excel.csv", data, "text/csv")
    assert answer.status_code in (200, 201), answer.text


def test_bad_row_rejects_the_whole_file_and_names_the_row():
    before = count_rows()
    data = csv_file(HEADER, f"{unique_email()},Arshad Test", "not-an-email,Mia Khan",
                    f"{unique_email()},Sam Lee")  # fmt: skip
    answer = upload(IMPORT_PATH, "customers.csv", data, "text/csv")
    assert answer.status_code == 400
    assert answer.json()["errors"][0]["row"] == 3  # row 1 is the header
    assert count_rows() == before, "rows before the bad one were saved"


def test_wrong_columns_are_refused():
    data = csv_file("mail,full_name", f"{unique_email()},Arshad Test")
    assert upload(IMPORT_PATH, "customers.csv", data, "text/csv").status_code == 400


def test_file_that_is_not_utf8_is_refused_clearly():
    data = "email,name\r\nzoe@example.com,Zoë\r\n".encode("cp1252")  # old Excel "CSV"
    answer = upload(IMPORT_PATH, "old-excel.csv", data, "text/csv")
    assert answer.status_code == 400
    assert answer.json().get("error"), "no message telling the user what to do"
