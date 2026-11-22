"""Check that every template file starts with the credit line.

When people copy a template into a work project, this one comment line tells
their teammates where it came from (brief section 7.7 and the growth plan):

    # Template from myOpenSDET: https://myopensdet.github.io/

Template files are the files inside any `templates/` folder under `modules/`
(and in `_new_topic_template/`). The comment uses each file type's own style:
`#` for Python, YAML, Gherkin, Robot Framework, shell and Dockerfiles, `//` for JavaScript and
Java, `--` for SQL, `<!-- -->` for Markdown, HTML and XML (JMeter plans).
A first line like `#!/usr/bin/env bash`, `<?xml ...?>` or `<!doctype html>` may come before it.
JSON, CSV and Excel files cannot hold comments, so they are skipped.

Usage (from the repository root):
    .venv/bin/python scripts/check_credit_lines.py          # list files without it
    .venv/bin/python scripts/check_credit_lines.py --fix    # add it where missing
"""

from __future__ import annotations

import sys
from pathlib import Path

SITE_URL = "https://myopensdet.github.io/"
TEXT = f"Template from myOpenSDET: {SITE_URL}"
ROOTS = (Path("modules"), Path("_new_topic_template/modules"))

HASH = ("#", "")
SLASHES = ("//", "")
DASHES = ("--", "")
MARKUP = ("<!--", " -->")
STYLE_BY_SUFFIX = {
    **dict.fromkeys(
        [
            ".py",
            ".sh",
            ".bash",
            ".yml",
            ".yaml",
            ".toml",
            ".feature",
            ".cfg",
            ".ini",
            ".txt",
            ".robot",
        ],
        HASH,
    ),
    **dict.fromkeys([".js", ".mjs", ".ts", ".java", ".kt", ".go", ".cs"], SLASHES),
    ".sql": DASHES,
    **dict.fromkeys([".md", ".html", ".xml", ".jmx"], MARKUP),
}
STYLE_BY_NAME = {
    "Dockerfile": HASH,
    "Makefile": HASH,
    ".env.example": HASH,
    "docker-compose.yml": HASH,
}
NO_COMMENTS = {".json", ".csv", ".gitkeep", ".png", ".jpg", ".svg", ".pdf", ".xlsx"}
PREAMBLE = ("#!", "<?xml", "<!doctype", "# -*- coding", "# syntax=")  # may stay above the credit


def credit_line(path: Path) -> str | None:
    """The exact credit line for this file, or None if the type takes no comments."""
    style = STYLE_BY_NAME.get(path.name) or STYLE_BY_SUFFIX.get(path.suffix)
    if style is None:
        return None
    start, end = style
    return f"{start} {TEXT}{end}"


def generated(path: Path) -> bool:
    """Files tools make by themselves (Python caches, editor files, the SQLite
    database a test run creates) are not templates."""
    hidden = path.name.startswith(".") and path.name not in STYLE_BY_NAME
    made_by_tests = path.suffix in (".sqlite3", ".db")
    return (
        hidden
        or made_by_tests
        or any(part in ("__pycache__", ".pytest_cache") for part in path.parts)
    )


def template_files() -> list[Path]:
    files = []
    for root in ROOTS:
        for folder in root.rglob("templates"):
            if folder.is_dir():
                files += [p for p in folder.rglob("*") if p.is_file() and not generated(p)]
    return sorted(files)


def has_credit(text: str, line: str) -> bool:
    lines = text.splitlines()
    if lines and lines[0].startswith(PREAMBLE):
        lines = lines[1:]
    return bool(lines) and lines[0].strip() == line


def add_credit(text: str, line: str) -> str:
    lines = text.splitlines(keepends=True)
    if lines and lines[0].startswith(PREAMBLE):
        return lines[0] + line + "\n" + "".join(lines[1:])
    return line + "\n" + text


def main() -> int:
    fix = "--fix" in sys.argv[1:]
    missing, unknown, checked = [], [], 0
    for path in template_files():
        if path.suffix in NO_COMMENTS or path.name in NO_COMMENTS:
            continue
        line = credit_line(path)
        if line is None:
            unknown.append(path)
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        if has_credit(text, line):
            continue
        if fix:
            path.write_text(add_credit(text, line), encoding="utf-8")
            print(f"  added   {path}")
        else:
            missing.append(path)
    print(f"check_credit_lines: {checked} template files checked")
    for path in unknown:
        print(f"  UNKNOWN TYPE  {path}  (add its comment style to scripts/check_credit_lines.py)")
    for path in missing:
        print(f"  MISSING  {path}")
    if missing or unknown:
        if missing:
            print("Add the line with: .venv/bin/python scripts/check_credit_lines.py --fix")
        return 1
    print("check_credit_lines: every template has the credit line")
    return 0


if __name__ == "__main__":
    sys.exit(main())
