# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 8: file handling. Replace each raise line with your code."""

import csv
from pathlib import Path


def read_device_ids(path: Path) -> list[str]:
    """Read one device ID per line. Strip spaces; skip empty lines and lines starting with "#"."""
    raise NotImplementedError("Write your code here")


def write_report(path: Path, lines: list[str]) -> None:
    """Write each line to the file, with a newline after each one."""
    raise NotImplementedError("Write your code here")


def load_cases(path: Path) -> list[dict]:
    """Read a CSV file with the columns device_id and expected_status.

    Return one dict per row, with expected_status as an int. The file may come
    from Excel, so open it with encoding="utf-8-sig".
    """
    raise NotImplementedError("Write your code here")
