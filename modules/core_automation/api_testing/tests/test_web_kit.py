# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""How the web works: the practice shop's HTML has no products, its REST API answers with
the status codes the page shows, and (with a browser) watch_requests.py finds the AJAX
call and tells a frontend bug from a backend bug."""

import json
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

KIT = Path(__file__).resolve().parents[1] / "templates" / "web_kit"
CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def shop(request):
    port = free_port()
    bug = getattr(request, "param", None)
    args = [sys.executable, "web_demo.py", "--port", str(port)] + (["--bug", bug] if bug else [])
    server = subprocess.Popen(args, cwd=KIT, stdout=subprocess.PIPE, text=True)
    assert "Practice shop" in server.stdout.readline()
    yield f"http://127.0.0.1:{port}"
    server.terminate()
    server.wait(timeout=10)


def call(url, method="GET", body=None, content_type="application/json"):
    data = None if body is None else body.encode()
    req = urllib.request.Request(url, data=data, method=method)  # noqa: S310 (local server)
    if data is not None:
        req.add_header("Content-Type", content_type)
    try:
        with urllib.request.urlopen(req, timeout=10) as answer:  # noqa: S310 (local test server)
            return answer.status, answer.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode()


def watch(url, *extra):
    return subprocess.run(
        [sys.executable, "watch_requests.py", url, *extra],
        cwd=KIT, capture_output=True, text=True, timeout=120,
    ).stdout  # fmt: skip


def browser_installed():
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            return Path(p.chromium.executable_path).exists()
    except Exception:  # noqa: BLE001 (any problem means: skip)
        return False


needs_browser = pytest.mark.skipif(not browser_installed(), reason="playwright install chromium")


@pytest.mark.parametrize("name", ["web_demo.py", "watch_requests.py", "page/app.js"])
def test_credit_line(name):
    assert CREDIT in "\n".join((KIT / name).read_text(encoding="utf-8").splitlines()[:3])


def test_html_has_no_products_but_the_api_does(shop):
    status, html = call(shop + "/")
    assert status == 200
    assert '<ul id="products"></ul>' in html
    assert "Test mug" not in html
    status, body = call(shop + "/api/products")
    assert json.loads(body)[1] == {"id": 2, "title": "Test mug", "price": 9.99, "stock": 12}


@pytest.mark.parametrize(
    ("method", "path", "body", "status", "answer"),
    [
        ("GET", "/api/products/2", None, 200, '"price": 9.99'),
        ("GET", "/api/products/9", None, 404, "product 9 not found"),
        ("POST", "/api/cart", '{"product_id": 2, "quantity": 2}', 201, '"total": 19.98'),
        ("POST", "/api/cart", '{"product_id": 3, "quantity": 1}', 422, "Bug sticker is sold out"),
        ("POST", "/api/cart", '{"product_id": 2, "quantity": 50}', 422, "quantity must be 1 to 12"),
        ("POST", "/api/cart", '{"product_id": 2, "quantity": 2', 400, "send JSON like"),
        ("DELETE", "/api/products/2", None, 405, "DELETE is not allowed"),
    ],
)
def test_rest_answers(shop, method, path, body, status, answer):
    got_status, got_body = call(shop + path, method, body)
    assert (got_status, answer in got_body) == (status, True), got_body


def test_form_data_is_refused_with_415(shop):
    status, body = call(shop + "/api/cart", "POST", "product_id=2", "text/plain")
    assert (status, "send JSON" in body) == (415, True)


@needs_browser
def test_watch_lists_the_ajax_call(shop):
    out = watch(shop)
    assert "fetch      GET    200    " + shop + "/api/products" in out
    assert "API calls made by JavaScript (AJAX): 1" in out
    assert "Not a full address" in watch(shop.removeprefix("http://"))


@needs_browser
@pytest.mark.parametrize(
    ("shop", "api_price", "page_shows"),
    [(None, '"price": 9.99', "Test mug £9.99"), ("frontend", '"price": 9.99', "Test mug £10"),
     ("backend", '"price": 99.9', "Test mug £99.90")],
    indirect=["shop"],
)  # fmt: skip
def test_frontend_or_backend_bug(shop, api_price, page_shows):
    out = watch(shop, "--find", "Test mug")
    assert api_price in out
    assert out.rstrip().endswith("The page shows: " + page_shows)


@needs_browser
def test_the_page_shows_the_api_error(shop):
    from playwright.sync_api import expect, sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(shop)
        page.get_by_label("Product").select_option("Bug sticker")
        page.get_by_role("button", name="Add to cart").click()
        expect(page.get_by_role("status")).to_have_text("Sorry: Bug sticker is sold out")
        browser.close()
