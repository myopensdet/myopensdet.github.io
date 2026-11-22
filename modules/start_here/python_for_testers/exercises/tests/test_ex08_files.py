# Template from myOpenSDET: https://myopensdet.github.io/
from ex08_files import read_usernames, write_report


def test_read_usernames(tmp_path):
    path = tmp_path / "users.txt"
    path.write_text("# test users\narshad\n\n  maria  \nআরশাদ\n", encoding="utf-8")
    assert read_usernames(path) == ["arshad", "maria", "আরশাদ"]


def test_write_report(tmp_path):
    path = tmp_path / "report.txt"
    write_report(path, ["2 passed", "1 failed"])
    assert path.read_text(encoding="utf-8") == "2 passed\n1 failed\n"
