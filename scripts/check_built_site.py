"""Check the built site the way GitHub Pages will serve it.

Serves site/ at / on a local port, opens every page and file it
can reach from the home page, and fails when:

- a page or file is missing (a broken link),
- a link leaves the site on the same server (it would 404 on Pages),
- a page loads a script, style, image or frame from another server
  (readers' browsers would contact it; everything should come from the site),
- a page lacks the Mermaid loader before the theme's script (without it, the
  theme fetches Mermaid from unpkg.com), or the pinned Mermaid file doesn't
  match the hash in the loader.

Links that people click to other sites are fine and are not checked here
(scripts/check_links.py --external does that).

Run after `zensical build`:

    .venv/bin/python scripts/check_built_site.py
    .venv/bin/python scripts/check_built_site.py path/to/other/site   # another folder
"""

import base64
import functools
import hashlib
import re
import sys
import threading
import urllib.error
import urllib.request
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE_PATH = "/"

# Link tags that only describe the page; they don't make the browser fetch anything.
DESCRIBING_RELS = {"canonical", "alternate", "author", "license", "me"}


class Links(HTMLParser):
    """Collect every link on a page, and every resource the page loads."""

    def __init__(self):
        super().__init__()
        self.links: list[str] = []
        self.loads: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        elif tag in ("script", "img", "iframe", "source", "audio", "video") and values.get("src"):
            self.loads.append(values["src"])
            self.links.append(values["src"])
        elif tag == "link" and values.get("href"):
            rels = set((values.get("rel") or "").lower().split())
            if not rels & DESCRIBING_RELS:
                self.loads.append(values["href"])
            self.links.append(values["href"])


def mermaid_problems(site: Path) -> list[str]:
    """The loader's pinned Mermaid file exists and matches its SHA-384 hash."""
    loader = site / "assets" / "javascripts" / "mermaid-loader.js"
    if not loader.is_file():
        return ["missing assets/javascripts/mermaid-loader.js"]
    text = loader.read_text(encoding="utf-8")
    version = re.search(r'var VERSION = "([^"]+)"', text)
    integrity = re.search(r'var INTEGRITY = "(sha384-[^"]+)"', text)
    if not (version and integrity):
        return ["mermaid-loader.js: VERSION or INTEGRITY not found"]
    vendored = loader.parent / "vendor" / f"mermaid-{version[1]}.min.js"
    if not vendored.is_file():
        return [f"missing {vendored.relative_to(site)}"]
    digest = base64.b64encode(hashlib.sha384(vendored.read_bytes()).digest()).decode()
    if f"sha384-{digest}" != integrity[1]:
        return [f"{vendored.name} doesn't match the INTEGRITY hash in mermaid-loader.js"]
    return []


def loader_problem(url: str, html: str) -> str | None:
    """The Mermaid loader must come before the theme's bundle on every page."""
    loader = html.find("assets/javascripts/mermaid-loader.js")
    bundle = html.find("assets/javascripts/bundle.")
    if bundle != -1 and (loader == -1 or loader > bundle):
        return f"no Mermaid loader before the theme's script: {url}"
    return None


class SiteHandler(SimpleHTTPRequestHandler):
    """Serve site/ at /, like GitHub Pages does."""

    def translate_path(self, path):
        clean = urlparse(path).path
        if not clean.startswith(BASE_PATH):
            return str(SITE / "does-not-exist")
        return super().translate_path("/" + clean[len(BASE_PATH) :])

    def log_message(self, *_):
        pass


def crawl(base: str, host: str) -> tuple[int, list[str]]:
    seen: set[str] = set()
    todo = [base]
    problems: list[str] = []
    while todo:
        url = todo.pop()
        if url in seen:
            continue
        seen.add(url)
        try:
            with urllib.request.urlopen(url, timeout=10) as response:  # noqa: S310 (local server only)
                body = response.read()
                is_html = "html" in response.headers.get("Content-Type", "")
        except urllib.error.HTTPError as error:
            problems.append(f"{error.code}: {url}")
            continue
        if not is_html:
            continue
        html = body.decode("utf-8", "replace")
        if problem := loader_problem(url, html):
            problems.append(problem)
        page = Links()
        page.feed(html)
        for load in page.loads:
            target = urlparse(urljoin(url, load))
            if target.scheme in ("http", "https") and target.netloc != host:
                problems.append(f"loads from another server ({target.netloc}): {url}")
        for link in page.links:
            full = urldefrag(urljoin(url, link))[0]
            target = urlparse(full)
            if target.scheme not in ("http", "https") or target.netloc != host:
                continue
            if not target.path.startswith(BASE_PATH):
                problems.append(f"link leaves {BASE_PATH} ({target.path}): {url}")
                continue
            todo.append(full)
    return len(seen), sorted(set(problems))


def main() -> int:
    global SITE
    if len(sys.argv) > 1:
        SITE = Path(sys.argv[1]).resolve()
    if not (SITE / "index.html").is_file():
        print("No built site. Run `.venv/bin/zensical build` first.")
        return 1
    handler = functools.partial(SiteHandler, directory=str(SITE))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    host = f"127.0.0.1:{server.server_address[1]}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        count, problems = crawl(f"http://{host}{BASE_PATH}", host)
    finally:
        server.shutdown()
    problems += mermaid_problems(SITE)
    shown = [problem.replace(f"http://{host}", "") for problem in problems]
    for problem in shown:
        print(" ", problem)
    if problems:
        print(f"check_built_site: {len(problems)} problem(s) in {count} pages and files")
        return 1
    print(f"check_built_site: {count} pages and files open at {BASE_PATH},", end=" ")
    print("nothing loaded from other servers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
