# Template from myOpenSDET: https://myopensdet.github.io/
"""A small bookshop web app: the app under test in the UI automation
and reporting lessons.

Replace it with your own app. It has what real web apps have: a login, a search
that takes a moment to answer, a cart, a confirm dialog, a checkout form with the
card field inside an iframe, and a link that opens a new tab. Everything is in
memory and fake. One bug is planted on purpose: removing a book on the cart page
doesn't update the cart count in the header.
"""

import asyncio
import itertools
import uuid
from decimal import Decimal
from html import escape
from typing import Literal

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

BOOKS = {
    "Python for Testers": Decimal("24.99"),
    "SQL in a Week": Decimal("19.50"),
    "Clean Tests": Decimal("31.00"),
    "Playwright Pocket Guide": Decimal("15.75"),
}
EXPRESS = Decimal("4.99")
COUNTRIES = ["Bangladesh", "Germany", "United Kingdom", "United States"]
USER = {"email": "tester@example.com", "password": "local_only_password"}
SEARCH_SECONDS = 0.8  # the search answers after a moment, like a real one

app = FastAPI(title="UI practice shop")
sessions: dict[str, dict[str, int]] = {}  # session id -> cart {book: copies}
orders: dict[str, dict] = {}
order_numbers = itertools.count(1001)

CSS = """
body { font-family: system-ui, sans-serif; max-width: 46rem; margin: 0 auto; padding: 1rem; }
header nav { display: flex; gap: 1rem; align-items: center; border-bottom: 1px solid #ccc;
             padding-bottom: .5rem; }
header form { margin-left: auto; }
[data-testid=cart-count] { background: #1d4ed8; color: #fff; border-radius: 1rem;
                           padding: 0 .5rem; }
#results { list-style: none; padding: 0; display: grid; gap: .5rem; }
#results li { border: 1px solid #ccc; padding: .5rem; }
label { display: block; margin-top: .5rem; }
iframe { border: 1px solid #ccc; height: 5rem; width: 100%; margin-top: .5rem; }
[role=alert] { color: #b91c1c; }
td, th { padding: .25rem .75rem; text-align: left; }
"""


def cart_of(request: Request) -> dict[str, int] | None:
    return sessions.get(request.cookies.get("session", ""))


def summary(cart: dict[str, int]) -> dict:
    lines = [
        {"book": b, "copies": n, "price": str(BOOKS[b]), "line_total": str(BOOKS[b] * n)}
        for b, n in cart.items()
    ]
    total = sum((BOOKS[b] * n for b, n in cart.items()), Decimal("0.00"))
    return {"lines": lines, "count": sum(cart.values()), "total": str(total)}


def page(title, body, cart=None, script="", status=200) -> HTMLResponse:
    header = ""
    if cart is not None:
        header = f"""<header><nav aria-label="Main">
  <a href="/books">Books</a>
  <a href="/cart">Cart</a> <span data-testid="cart-count">{summary(cart)["count"]}</span>
  <form method="post" action="/logout"><button>Log out</button></form>
</nav></header>"""
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} - Practice shop</title><style>{CSS}</style></head>
<body>{header}<main>{body}</main><script>{script}</script></body></html>"""
    return HTMLResponse(html, status_code=status)


def need_cart(request: Request) -> dict[str, int]:
    cart = cart_of(request)
    if cart is None:
        raise HTTPException(401, "Log in first")
    return cart


def new_session(response, email: str, password: str) -> bool:
    if (email, password) != (USER["email"], USER["password"]):
        return False
    session = uuid.uuid4().hex
    sessions[session] = {}
    response.set_cookie("session", session, httponly=True, samesite="lax")
    return True


# ---- Log in and out ----

LOGIN_FORM = """<h1>Log in</h1>{alert}
<form method="post" action="/login">
  <label for="email">Email</label><input id="email" name="email" type="email">
  <label for="password">Password</label><input id="password" name="password" type="password">
  <p><button>Log in</button></p>
</form>"""


@app.get("/")
def home():
    return RedirectResponse("/books", status_code=303)


@app.get("/login")
def login_page():
    return page("Log in", LOGIN_FORM.format(alert=""))


@app.post("/login")
def login(email: str = Form(""), password: str = Form("")):
    response = RedirectResponse("/books", status_code=303)
    if new_session(response, email, password):
        return response
    alert = '<p role="alert">Wrong email or password</p>'
    return page("Log in", LOGIN_FORM.format(alert=alert), status=401)


@app.post("/logout")
def logout(request: Request):
    sessions.pop(request.cookies.get("session", ""), None)
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie("session")
    return response


# ---- Books: the list loads, and searches, after the page has loaded ----

BOOKS_SCRIPT = """
const results = document.getElementById('results');
const status = document.getElementById('status');
const count = document.querySelector('[data-testid=cart-count]');
let latest = 0;
async function load(q) {
  const mine = ++latest;
  status.textContent = 'Loading books...';
  const books = await (await fetch('/api/books?q=' + encodeURIComponent(q))).json();
  if (mine !== latest) return;  // a newer search started: drop this older answer
  results.replaceChildren();
  status.textContent = books.length
    ? books.length + (books.length === 1 ? ' book' : ' books')
    : 'No books match "' + q + '"';
  for (const book of books) {
    const item = document.createElement('li');
    const title = document.createElement('h2');
    title.textContent = book.title;
    const price = document.createElement('p');
    price.textContent = 'Price: ' + book.price;
    const add = document.createElement('button');
    add.textContent = 'Add to cart';
    add.onclick = async () => {
      const response = await fetch('/api/cart', {method: 'POST',
        headers: {'Content-Type': 'application/json'}, body: JSON.stringify({book: book.title})});
      count.textContent = (await response.json()).count;
      status.textContent = 'Added ' + book.title + ' to your cart';
    };
    item.append(title, price, add);
    results.append(item);
  }
}
document.getElementById('search').onsubmit = (event) => {
  event.preventDefault();
  load(document.getElementById('q').value);
};
load('');
"""


@app.get("/books")
def books_page(request: Request):
    cart = cart_of(request)
    if cart is None:
        return RedirectResponse("/login", status_code=303)
    body = """<h1>Books</h1>
<form id="search" role="search">
  <label for="q">Search books</label><input id="q" name="q" type="search">
  <button>Search</button>
</form>
<p id="status" role="status"></p>
<ul id="results" aria-label="Books"></ul>"""
    return page("Books", body, cart, BOOKS_SCRIPT)


# ---- Cart: remove a book, or empty it after a confirm dialog ----

CART_SCRIPT = """
for (const button of document.querySelectorAll('button[data-book]')) {
  button.onclick = async () => {
    const book = button.dataset.book;
    const cart = await (await fetch('/api/cart/' + encodeURIComponent(book),
                                    {method: 'DELETE'})).json();
    button.closest('tr').remove();
    document.getElementById('total').textContent = cart.total;
    // Planted bug: the header's cart count should change to cart.count here too.
  };
}
const empty = document.getElementById('empty');
if (empty) empty.onclick = async () => {
  if (!confirm('Empty your cart?')) return;
  await fetch('/api/cart', {method: 'DELETE'});
  location.reload();
};
"""


@app.get("/cart")
def cart_page(request: Request):
    cart = cart_of(request)
    if cart is None:
        return RedirectResponse("/login", status_code=303)
    if not cart:
        return page("Cart", "<h1>Your cart</h1><p>Your cart is empty.</p>", cart)
    s = summary(cart)
    rows = "".join(
        f"""<tr><td>{escape(line["book"])}</td><td>{line["copies"]}</td>
<td>{line["line_total"]}</td>
<td><button data-book="{escape(line["book"])}">Remove</button></td></tr>"""
        for line in s["lines"]
    )
    body = f"""<h1>Your cart</h1>
<table><thead><tr><th>Book</th><th>Copies</th><th>Price</th><th></th></tr></thead>
<tbody>{rows}</tbody></table>
<p>Total: <strong id="total" data-testid="cart-total">{s["total"]}</strong></p>
<p><button id="empty">Empty cart</button> <a href="/checkout">Go to checkout</a></p>"""
    return page("Cart", body, cart, CART_SCRIPT)


# ---- Checkout: a form, a card field in an iframe, terms in a new tab ----

CHECKOUT_SCRIPT = """
document.getElementById('checkout').onsubmit = async (event) => {
  event.preventDefault();
  const frame = document.querySelector('iframe').contentDocument;
  const order = {
    name: document.getElementById('name').value,
    country: document.getElementById('country').value,
    delivery: document.querySelector('input[name=delivery]:checked').value,
    terms: document.getElementById('terms').checked,
    card: frame.getElementById('card').value,
  };
  const response = await fetch('/api/orders', {method: 'POST',
    headers: {'Content-Type': 'application/json'}, body: JSON.stringify(order)});
  const answer = await response.json();
  if (response.ok) location = '/orders/' + answer.number;
  else document.getElementById('error').textContent = answer.detail;
};
"""


@app.get("/checkout")
def checkout_page(request: Request):
    cart = cart_of(request)
    if cart is None:
        return RedirectResponse("/login", status_code=303)
    countries = "".join(f"<option>{c}</option>" for c in COUNTRIES)
    body = f"""<h1>Checkout</h1>
<form id="checkout">
  <label for="name">Full name</label><input id="name" autocomplete="name">
  <label for="country">Country</label>
  <select id="country"><option value="">Choose...</option>{countries}</select>
  <fieldset><legend>Delivery</legend>
    <label><input type="radio" name="delivery" value="standard" checked> Standard (free)</label>
    <label><input type="radio" name="delivery" value="express"> Express ({EXPRESS})</label>
  </fieldset>
  <iframe src="/payment-frame" title="Payment"></iframe>
  <label><input type="checkbox" id="terms">
    I accept the <a href="/terms" target="_blank">terms of sale</a></label>
  <p id="error" role="alert"></p>
  <button>Place order</button>
</form>"""
    return page("Checkout", body, cart, CHECKOUT_SCRIPT)


@app.get("/payment-frame")
def payment_frame():
    """The card field lives in its own page, shown in an iframe, like real payment forms."""
    body = """<label for="card">Card number</label>
<input id="card" inputmode="numeric" autocomplete="cc-number">"""
    return page("Payment", body)


@app.get("/terms")
def terms_page():
    body = """<h1>Terms of sale</h1>
<p>This is a practice shop. Nothing is sold, and no card is charged.</p>"""
    return page("Terms of sale", body)


@app.get("/orders/{number}")
def order_page(number: str, request: Request):
    order = orders.get(number)
    if order is None or order["session"] != request.cookies.get("session"):
        return page("Not found", "<h1>No such order</h1>", status=404)
    body = f"""<h1>Thank you for your order</h1>
<p>Order number: <strong data-testid="order-number">{number}</strong></p>
<p>Delivery: {order["delivery"].title()}</p>
<p>Total paid: {order["total"]}</p>"""
    return page("Order " + number, body, sessions.get(order["session"], {}))


# ---- API: the pages above call it; tests can too, to set things up fast ----


class Login(BaseModel):
    email: str
    password: str


class NewItem(BaseModel):
    book: str


class NewOrder(BaseModel):
    name: str
    country: str
    delivery: Literal["standard", "express"]
    terms: bool
    card: str


@app.post("/api/login")
def api_login(login: Login):
    response = JSONResponse({"message": "Logged in"})
    if not new_session(response, login.email, login.password):
        raise HTTPException(401, "Wrong email or password")
    return response


@app.get("/api/books")
async def api_books(q: str = ""):
    await asyncio.sleep(SEARCH_SECONDS)
    return [
        {"title": title, "price": str(price)}
        for title, price in BOOKS.items()
        if q.lower() in title.lower()
    ]


@app.get("/api/cart")
def api_cart(request: Request):
    return summary(need_cart(request))


@app.post("/api/cart")
def api_add(item: NewItem, request: Request):
    cart = need_cart(request)
    if item.book not in BOOKS:
        raise HTTPException(400, f"No book called {item.book}")
    cart[item.book] = cart.get(item.book, 0) + 1
    return summary(cart)


@app.delete("/api/cart/{book}")
def api_remove(book: str, request: Request):
    cart = need_cart(request)
    cart.pop(book, None)
    return summary(cart)


@app.delete("/api/cart")
def api_empty(request: Request):
    cart = need_cart(request)
    cart.clear()
    return summary(cart)


@app.post("/api/orders", status_code=201)
def api_order(order: NewOrder, request: Request):
    cart = need_cart(request)
    digits = order.card.replace(" ", "")
    problems = [
        (not cart, "Your cart is empty"),
        (not order.name.strip(), "Enter your full name"),
        (order.country not in COUNTRIES, "Choose a country"),
        (not order.terms, "Please accept the terms of sale"),
        (not (digits.isdigit() and len(digits) == 16), "Card number must have 16 digits"),
    ]
    for failed, message in problems:
        if failed:
            raise HTTPException(400, message)
    total = Decimal(summary(cart)["total"]) + (EXPRESS if order.delivery == "express" else 0)
    number = f"BK-{next(order_numbers)}"
    orders[number] = {
        "session": request.cookies.get("session"),
        "delivery": order.delivery,
        "total": str(total),
    }
    cart.clear()
    return {"number": number, "total": str(total)}
