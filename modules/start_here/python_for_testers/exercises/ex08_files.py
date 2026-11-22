# Template from myOpenSDET: https://myopensdet.github.io/
"""Exercise 8: reading and writing files."""

from pathlib import Path


def read_usernames(path: Path) -> list[str]:
    """Read one username per line. Skip empty lines and lines starting with "#"."""
    raise NotImplementedError("Write your code here")


def write_report(path: Path, lines: list[str]) -> None:
    """Write each line to the file, with a newline after each one."""
    raise NotImplementedError("Write your code here")
