"""Add a Content-Security-Policy to every page in site/.

Why: the policy tells the browser to run only the scripts this site ships.
If someone ever slips a script into a page (or a library tries to load one
from another server), the browser refuses to run it.

GitHub Pages can't send custom HTTP headers, so the policy goes in a
<meta http-equiv="Content-Security-Policy"> tag at the top of each page.
A meta tag has limits: it can't set `frame-ancestors` (who may show the site
in a frame) or reporting. Those need a real header.

The theme puts a few small scripts straight into each page (theme colour,
tabs, settings). Each one is allowed by its SHA-256 hash, so only that exact
text can run. One policy lists the hashes from every page, because the theme
swaps pages without a reload (instant navigation) and keeps the first
page's policy. The forwarding pages for old addresses (made by
scripts/build_redirects.py) are never swapped in, so each one gets a policy
with only its own script.

Run after `zensical build` and scripts/build_redirects.py, from the
repository root:
    .venv/bin/python scripts/build_csp.py
"""

from __future__ import annotations

import base64
import hashlib
import re
import sys
from pathlib import Path

SITE = Path("site")

# <script> with no src attribute and no JSON type: code that runs in the page.
INLINE_SCRIPT = re.compile(r"<script(?P<attrs>[^>]*)>(?P<code>.*?)</script>", re.S)
CHARSET = re.compile(r'<meta charset="utf-8">', re.I)
MARK = 'http-equiv="Content-Security-Policy"'

POLICY = [
    "default-src 'self'",
    "script-src 'self' {hashes}",
    # Mermaid diagrams and the theme set styles from JavaScript.
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data:",
    "font-src 'self'",
    # The repository box in the header reads stars and forks from GitHub.
    "connect-src 'self' https://api.github.com",
    "worker-src 'self'",
    "frame-src 'none'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "upgrade-insecure-requests",
]


def inline_scripts(text: str) -> list[str]:
    found = []
    for match in INLINE_SCRIPT.finditer(text):
        attrs = match.group("attrs")
        if "src=" in attrs or "application/json" in attrs:
            continue
        found.append(match.group("code"))
    return found


def is_forwarding(text: str) -> bool:
    """A small page from scripts/build_redirects.py that sends readers on."""
    return 'http-equiv="refresh"' in text


def sha256(code: str) -> str:
    digest = hashlib.sha256(code.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode("ascii") + "'"


def main() -> int:
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        print("build_csp: no pages in site/, run zensical build first", file=sys.stderr)
        return 1
    texts = {page: page.read_text(encoding="utf-8") for page in pages}
    theme = [text for text in texts.values() if not is_forwarding(text)]
    hashes = sorted({sha256(code) for text in theme for code in inline_scripts(text)})
    problems = []
    for page, text in texts.items():
        if MARK in text:
            continue  # already added (the script was run twice)
        allowed = hashes
        if is_forwarding(text):
            allowed = sorted({sha256(code) for code in inline_scripts(text)})
        policy = "; ".join(POLICY).format(hashes=" ".join(allowed))
        tag = f'<meta {MARK} content="{policy}">'
        new, count = CHARSET.subn(lambda m, tag=tag: m.group(0) + "\n      " + tag, text, count=1)
        if count != 1:
            problems.append(str(page))
            continue
        page.write_text(new, encoding="utf-8")
    if problems:
        print("build_csp: no <meta charset> in:\n  " + "\n  ".join(problems), file=sys.stderr)
        return 1
    print(f"build_csp: policy added to {len(pages)} pages ({len(hashes)} theme scripts allowed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
