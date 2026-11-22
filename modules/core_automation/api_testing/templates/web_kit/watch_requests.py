# Template from myOpenSDET: https://myopensdet.github.io/
"""Open a page in a real browser and list every request it makes, like the Network tab.

Shows which API calls happen behind a page (AJAX), and what JSON came back, so you
can tell a frontend bug (the API is right, the page is wrong) from a backend bug (the
API is already wrong). Works on any page you may test.

Needs: pip install playwright, then: playwright install chromium
Usage:
    python watch_requests.py http://127.0.0.1:8797
    python watch_requests.py http://127.0.0.1:8797 --find "Test mug"
"""

import argparse
import sys

from playwright.sync_api import Error, Response, sync_playwright

API_TYPES = {"fetch", "xhr"}  # the requests JavaScript makes: AJAX


def main() -> int:
    parser = argparse.ArgumentParser(description="List the requests a page makes.")
    parser.add_argument("url", help="the page to open, like https://shop.example.com/products")
    parser.add_argument("--find", help="also print the page's line that has this text")
    args = parser.parse_args()
    if not args.url.startswith(("http://", "https://")):
        print(f"Not a full address: '{args.url}'. Start with http:// or https://")
        return 2

    seen: list[Response] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("response", lambda response: seen.append(response))
        try:
            page.goto(args.url, wait_until="networkidle", timeout=30_000)
        except Error as err:
            print(f"Could not open the page: {err.message.splitlines()[0]}")
            return 1

        print(f"{'#':>2}  {'type':<10} {'method':<6} {'status':<6} address")
        for number, response in enumerate(seen, 1):
            request = response.request
            print(f"{number:>2}  {request.resource_type:<10} {request.method:<6} "
                  f"{response.status:<6} {response.url}")  # fmt: skip

        calls = [r for r in seen if r.request.resource_type in API_TYPES]
        print(f"\nAPI calls made by JavaScript (AJAX): {len(calls)}")
        for response in calls:
            body = response.text()
            print(f"  {response.request.method} {response.url} -> {response.status}")
            print(f"  answer: {body[:300]}{' ...' if len(body) > 300 else ''}")

        if args.find:
            line = page.get_by_text(args.find).first
            shown = line.inner_text() if line.count() else "(not on the page)"
            print(f"\nThe page shows: {shown}")
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
