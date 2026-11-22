"""Write a small forwarding page at every old address listed in data/redirects.yml.

Why: published addresses never break. When a page moves, its old address keeps
working: it sends the reader (and search engines) to the new one.

Run after `zensical build`, from the repository root:
    .venv/bin/python scripts/build_redirects.py

It fails if a target page does not exist in site/, or if an old address is
still a real page (then the redirect would hide it).
"""

from __future__ import annotations

import html
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlparse

import yaml  # PyYAML, already installed with Zensical (requirements-docs.txt)

SITE = Path("site")
REDIRECTS = Path("data/redirects.yml")
CONFIG = Path("zensical.toml")

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>This page has moved</title>
  <meta name="robots" content="noindex">
  <link rel="canonical" href="{canonical}">
  <meta http-equiv="refresh" content="0; url={target}">
  <script>location.replace({target_js} + location.hash);</script>
</head>
<body>
  <p>This page has moved to <a href="{target}">{target}</a>.</p>
</body>
</html>
"""


def main() -> int:
    site_url = tomllib.loads(CONFIG.read_text(encoding="utf-8"))["project"]["site_url"]
    base = urlparse(site_url).path  # "/" for a site at the root of its domain
    redirects = yaml.safe_load(REDIRECTS.read_text(encoding="utf-8")) or {}
    problems = []
    for old, new in redirects.items():
        old, new = str(old).strip("/"), str(new).strip("/")
        new_file = SITE / new / "index.html" if new else SITE / "index.html"
        old_file = SITE / old / "index.html"
        if not new_file.exists():
            problems.append(f"{old}/ -> {new}/: the new page does not exist")
            continue
        if old_file.exists():
            problems.append(f"{old}/ is still a real page; remove its redirect line")
            continue
        target = base + (new + "/" if new else "")
        old_file.parent.mkdir(parents=True, exist_ok=True)
        old_file.write_text(
            PAGE.format(
                canonical=html.escape(site_url + (new + "/" if new else "")),
                target=html.escape(target),
                target_js=repr(target).replace("'", '"'),
            ),
            encoding="utf-8",
        )
    if problems:
        print("build_redirects: " + "\n  ".join(["problems:", *problems]), file=sys.stderr)
        return 1
    print(f"build_redirects: {len(redirects)} old addresses forward to their new pages")
    return 0


if __name__ == "__main__":
    sys.exit(main())
