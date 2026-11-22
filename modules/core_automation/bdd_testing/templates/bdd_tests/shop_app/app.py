# Template from myOpenSDET: https://myopensdet.github.io/
"""A tiny bookshop with an API and a web page: the app under test in the BDD lessons.

Replace it with your own app. It keeps carts in memory and has one bug planted on
purpose: a coupon can be applied twice.
"""

import uuid
from decimal import ROUND_HALF_UP, Decimal
from html import escape

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

BOOKS = {"Python for Testers": Decimal("24.99"), "SQL in a Week": Decimal("19.50")}
COUPONS = {"SAVE10": Decimal("0.90")}
CENT = Decimal("0.01")

app = FastAPI(title="BDD practice shop")
carts: dict[str, dict] = {}


class ShopError(Exception):
    """A rule the shopper broke. The API answers 400 with it; the page shows it."""


def new_cart() -> str:
    cart_id = uuid.uuid4().hex
    carts[cart_id] = {"lines": {}, "coupons": [], "message": ""}
    return cart_id


def get_cart(cart_id: str) -> dict:
    if cart_id not in carts:
        raise HTTPException(404, "No such cart")
    return carts[cart_id]


def add_book(cart: dict, book: str, copies: int) -> None:
    if book not in BOOKS:
        raise ShopError(f"No book called {book}")
    if not 1 <= copies <= 10:
        raise ShopError("You can add 1 to 10 copies")
    cart["lines"][book] = cart["lines"].get(book, 0) + copies
    cart["message"] = f"Added {copies} x {book}"


def apply_coupon(cart: dict, code: str) -> None:
    if code not in COUPONS:
        raise ShopError(f"Unknown coupon: {code}")
    # Planted bug: the rule is one use per order, so this should refuse a coupon
    # that is already in cart["coupons"]. Instead the discount is applied again.
    cart["coupons"].append(code)
    cart["message"] = f"Coupon {code} applied"


def total(cart: dict) -> Decimal:
    amount = sum((BOOKS[b] * n for b, n in cart["lines"].items()), Decimal("0"))
    for code in cart["coupons"]:
        amount = amount * COUPONS[code]
    return amount.quantize(CENT, rounding=ROUND_HALF_UP)


def summary(cart_id: str) -> dict:
    cart = carts[cart_id]
    return {
        "id": cart_id,
        "lines": cart["lines"],
        "coupons": cart["coupons"],
        "total": str(total(cart)),
        "message": cart["message"],
    }


# ---- API ----


class NewItem(BaseModel):
    book: str
    copies: int


class NewCoupon(BaseModel):
    code: str


@app.post("/api/carts", status_code=201)
def api_new_cart():
    return summary(new_cart())


@app.get("/api/carts/{cart_id}")
def api_get_cart(cart_id: str):
    get_cart(cart_id)
    return summary(cart_id)


@app.post("/api/carts/{cart_id}/items")
def api_add_item(cart_id: str, item: NewItem):
    try:
        add_book(get_cart(cart_id), item.book, item.copies)
    except ShopError as error:
        raise HTTPException(400, str(error)) from None
    return summary(cart_id)


@app.post("/api/carts/{cart_id}/coupon")
def api_apply_coupon(cart_id: str, coupon: NewCoupon):
    try:
        apply_coupon(get_cart(cart_id), coupon.code)
    except ShopError as error:
        raise HTTPException(400, str(error)) from None
    return summary(cart_id)


# ---- Web page: plain forms, no JavaScript ----


@app.get("/shop")
def page_new_cart():
    return RedirectResponse(f"/shop/{new_cart()}", status_code=303)


@app.get("/shop/{cart_id}", response_class=HTMLResponse)
def page_cart(cart_id: str):
    cart = get_cart(cart_id)
    options = "".join(f"<option>{escape(b)}</option>" for b in BOOKS)
    lines = (
        "".join(f"<li>{n} x {escape(b)}</li>" for b, n in cart["lines"].items())
        or "<li>Your cart is empty</li>"
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Practice shop</title></head>
<body>
  <h1>Your cart</h1>
  <p role="status">{escape(cart["message"])}</p>
  <form method="post" action="/shop/{cart_id}/items">
    <label>Book <select name="book">{options}</select></label>
    <label>Copies <input name="copies" type="number" value="1"></label>
    <button>Add to cart</button>
  </form>
  <ul aria-label="Cart lines">{lines}</ul>
  <form method="post" action="/shop/{cart_id}/coupon">
    <label>Coupon <input name="code"></label>
    <button>Apply coupon</button>
  </form>
  <p>Total: <strong data-testid="total">{total(cart)}</strong></p>
</body></html>"""


@app.post("/shop/{cart_id}/items")
def page_add_item(cart_id: str, book: str = Form(...), copies: int = Form(...)):
    cart = get_cart(cart_id)
    try:
        add_book(cart, book, copies)
    except ShopError as error:
        cart["message"] = str(error)
    return RedirectResponse(f"/shop/{cart_id}", status_code=303)


@app.post("/shop/{cart_id}/coupon")
def page_apply_coupon(cart_id: str, code: str = Form(...)):
    cart = get_cart(cart_id)
    try:
        apply_coupon(cart, code)
    except ShopError as error:
        cart["message"] = str(error)
    return RedirectResponse(f"/shop/{cart_id}", status_code=303)
