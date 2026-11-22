# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""A small bookshop API: the app under test in the API + database lessons.

It has two bugs planted on purpose, for the lessons to find. Don't copy it into real work.
Run it on your own computer only:

    uvicorn app:app --host 127.0.0.1 --port 8090
"""

import os
import time
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path

import psycopg
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent


def connect() -> psycopg.Connection:
    return psycopg.connect(os.environ["DATABASE_URL"], row_factory=dict_row, autocommit=True)


@asynccontextmanager
async def lifespan(_app):
    with connect() as conn:
        conn.execute((HERE / "schema.sql").read_text(encoding="utf-8"))
    yield


app = FastAPI(title="Bookshop API (practice)", lifespan=lifespan)


class NewCustomer(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    full_name: str = Field(min_length=1, max_length=100)


class NewOrder(BaseModel):
    customer_id: int
    book_id: int
    quantity: int = Field(gt=0, le=10)
    unit_price: Decimal | None = None  # planted bug 1 uses this


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/customers", status_code=201)
def create_customer(body: NewCustomer):
    with connect() as conn:
        # Planted bug 2: the email is saved as sent, so "ARSHAD@example.com" gets past
        # the unique rule next to "arshad@example.com".
        try:
            return conn.execute(
                "INSERT INTO customers (email, full_name) VALUES (%s, %s) "
                "RETURNING id, email, full_name",
                (body.email, body.full_name),
            ).fetchone()
        except psycopg.errors.UniqueViolation:
            raise HTTPException(409, "A customer with this email already exists") from None


@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    with connect() as conn:
        row = conn.execute(
            "SELECT id, email, full_name FROM customers WHERE id = %s", (customer_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(404, "Customer not found")
    return row


def log_event(order_id: int, event: str) -> None:
    """Runs after the answer is sent, like a real app's background job."""
    time.sleep(0.5)
    with connect() as conn:
        conn.execute(
            "INSERT INTO order_events (order_id, event) VALUES (%s, %s)", (order_id, event)
        )


@app.post("/orders", status_code=201)
def create_order(body: NewOrder, background: BackgroundTasks):
    with connect() as conn, conn.transaction():
        book = conn.execute(
            "SELECT price, stock FROM books WHERE id = %s FOR UPDATE", (body.book_id,)
        ).fetchone()
        customer = conn.execute(
            "SELECT id FROM customers WHERE id = %s", (body.customer_id,)
        ).fetchone()
        if book is None or customer is None:
            raise HTTPException(404, "Book or customer not found")
        if book["stock"] < body.quantity:
            raise HTTPException(409, "Not enough stock")
        # Planted bug 1: a price sent by the client wins over the book's real price.
        price = body.unit_price if body.unit_price is not None else book["price"]
        conn.execute(
            "UPDATE books SET stock = stock - %s WHERE id = %s", (body.quantity, body.book_id)
        )
        order = conn.execute(
            "INSERT INTO orders (customer_id, book_id, quantity, unit_price, total) "
            "VALUES (%s, %s, %s, %s, %s) "
            "RETURNING id, customer_id, book_id, quantity, unit_price, total, status",
            (body.customer_id, body.book_id, body.quantity, price, price * body.quantity),
        ).fetchone()
    background.add_task(log_event, order["id"], "order_created")
    return order


@app.get("/orders/{order_id}")
def get_order(order_id: int):
    with connect() as conn:
        row = conn.execute(
            "SELECT id, customer_id, book_id, quantity, unit_price, total, status "
            "FROM orders WHERE id = %s",
            (order_id,),
        ).fetchone()
    if row is None:
        raise HTTPException(404, "Order not found")
    return row


@app.delete("/orders/{order_id}", status_code=204)
def delete_order(order_id: int):
    with connect() as conn, conn.transaction():
        order = conn.execute(
            "DELETE FROM orders WHERE id = %s RETURNING book_id, quantity", (order_id,)
        ).fetchone()
        if order is None:
            raise HTTPException(404, "Order not found")
        conn.execute(
            "UPDATE books SET stock = stock + %s WHERE id = %s",
            (order["quantity"], order["book_id"]),
        )
    return Response(status_code=204)
