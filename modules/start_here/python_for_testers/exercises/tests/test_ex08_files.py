# Template from myOpenSDET: https://myopensdet.github.io/
from ex08_files import load_cases, read_device_ids, write_report


def test_read_device_ids(tmp_path):
    path = tmp_path / "devices.txt"
    path.write_text("# devices in Lab 2\nSNS-0041\n\n  SNS-0042  \nগেটওয়ে-01\n", encoding="utf-8")
    assert read_device_ids(path) == ["SNS-0041", "SNS-0042", "গেটওয়ে-01"]


def test_write_report(tmp_path):
    path = tmp_path / "report.txt"
    write_report(path, ["2 passed", "1 failed"])
    assert path.read_text(encoding="utf-8") == "2 passed\n1 failed\n"


def test_load_cases_converts_the_status(tmp_path):
    path = tmp_path / "cases.csv"
    path.write_text("device_id,expected_status\nSNS-0041,200\nSNS-0043,404\n", encoding="utf-8")
    assert load_cases(path) == [
        {"device_id": "SNS-0041", "expected_status": 200},
        {"device_id": "SNS-0043", "expected_status": 404},
    ]


def test_load_cases_from_excel(tmp_path):
    path = tmp_path / "cases.csv"
    path.write_text("device_id,expected_status\nSNS-0041,200\n", encoding="utf-8-sig")
    assert load_cases(path)[0]["device_id"] == "SNS-0041"
