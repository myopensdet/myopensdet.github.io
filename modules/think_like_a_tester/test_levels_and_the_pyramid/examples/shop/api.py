# Template from myOpenSDET: https://myopensdet.github.io/
"""A small web API around the cart, so it can be tested the way other programs use it."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from shop.cart import Cart

app = FastAPI(title="Tiny shop")


class Line(BaseModel):
    name: str
    price_cents: int = Field(ge=1)
    quantity: int = Field(default=1, ge=1, le=10)


class Order(BaseModel):
    lines: list[Line]
    coupon: str | None = None


@app.post("/api/cart/totals")
def cart_totals(order: Order) -> dict[str, int]:
    cart = Cart(coupon=order.coupon)
    for line in order.lines:
        cart.add(line.name, line.price_cents, line.quantity)
    try:
        return cart.totals()
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from None
