# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Exercise 8: reading and writing files."""

from pathlib import Path


def read_usernames(path: Path) -> list[str]:
    """Read one username per line. Skip empty lines and lines starting with "#"."""
    names = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            names.append(line)
    return names


def write_report(path: Path, lines: list[str]) -> None:
    """Write each line to the file, with a newline after each one."""
    Path(path).write_text("".join(line + "\n" for line in lines), encoding="utf-8")
