# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""File upload: allowed files go in; empty, too big, wrong and disguised files don't."""

import pytest

from tests.conftest import MAX_BYTES, PDF, PNG, UPLOAD_PATH, upload


@pytest.mark.parametrize(
    ("name", "data", "mime"),
    [("photo.png", PNG, "image/png"), ("invoice.pdf", PDF, "application/pdf")],
    ids=["png", "pdf"],
)
def test_allowed_file_is_accepted(name, data, mime):
    answer = upload(UPLOAD_PATH, name, data, mime)
    assert answer.status_code == 201, answer.text
    assert answer.json()["size"] == len(data)


def test_file_exactly_at_the_limit_is_accepted():
    data = PNG + b"\0" * (MAX_BYTES - len(PNG))
    assert upload(UPLOAD_PATH, "big.png", data, "image/png").status_code == 201


def test_file_one_byte_over_the_limit_is_refused():
    data = PNG + b"\0" * (MAX_BYTES - len(PNG) + 1)
    answer = upload(UPLOAD_PATH, "too-big.png", data, "image/png")
    assert answer.status_code in (400, 413), f"{answer.status_code}: {answer.text}"


def test_empty_file_is_refused():
    assert upload(UPLOAD_PATH, "empty.png", b"", "image/png").status_code == 400


@pytest.mark.parametrize("name", ["notes.txt", "setup.exe", "photo.png.exe", "page.html"])
def test_file_type_not_on_the_list_is_refused(name):
    answer = upload(UPLOAD_PATH, name, b"some content")
    assert answer.status_code in (400, 415), f"{name} got {answer.status_code}"


def test_file_with_a_false_name_is_refused():
    """A text file renamed to .png must not pass as a picture."""
    answer = upload(UPLOAD_PATH, "photo.png", b"<script>alert(1)</script>", "image/png")
    assert answer.status_code in (400, 415), f"accepted: {answer.text}"


def test_folder_part_of_the_name_is_dropped():
    answer = upload(UPLOAD_PATH, "../../photo.png", PNG, "image/png")
    assert answer.status_code == 201
    assert "/" not in answer.json()["name"] and ".." not in answer.json()["name"]
