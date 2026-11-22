# Template from myOpenSDET: https://myopensdet.github.io/
from ex02_collections import clean_message, missing_devices, missing_fields, status_of


def test_clean_message():
    assert clean_message("  Saved! ") == "saved!"
    assert clean_message("ONLINE\n") == "online"


def test_missing_devices():
    expected = ["SNS-0041", "SNS-0042", "SNS-0043"]
    reported = ["SNS-0043", "SNS-0042", "SNS-0042"]
    assert missing_devices(expected, reported) == ["SNS-0041"]


def test_no_missing_devices():
    assert missing_devices(["SNS-0042"], ["SNS-0042", "SNS-0099"]) == []


def test_missing_fields():
    response = {"id": "SNS-0042", "status": "online"}
    assert missing_fields(response, ["id", "status", "battery", "last_seen"]) == [
        "battery",
        "last_seen",
    ]


def test_status_of():
    assert status_of({"id": "SNS-0042", "status": "offline"}) == "offline"
    assert status_of({"id": "SNS-0042"}) == "unknown"
