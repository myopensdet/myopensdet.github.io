# Template from myOpenSDET: https://myopensdet.github.io/
"""A small book API on PostgreSQL: the app the test container checks."""

import os
from contextlib import asynccontextmanager
from decimal import Decimal

import psycopg
from fastapi import FastAPI, HTTPException
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

DATABASE_URL = os.environ["DATABASE_URL"]


def connect():
    return psycopg.connect(DATABASE_URL, autocommit=True, row_factory=dict_row)


@asynccontextmanager
async def lifespan(app):
    with connect() as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS books ("
            " id SERIAL PRIMARY KEY, title TEXT NOT NULL, price NUMERIC(8, 2) NOT NULL)"
        )
    yield


app = FastAPI(title="Books API", lifespan=lifespan)


class NewBook(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0, max_digits=8, decimal_places=2)


@app.get("/health")
def health():
    try:
        with connect() as db:
            db.execute("SELECT 1")
    except psycopg.OperationalError:
        raise HTTPException(503, "The database is not reachable") from None
    return {"status": "ok", "database": "up"}


@app.post("/books", status_code=201)
def add_book(book: NewBook):
    with connect() as db:
        return db.execute(
            "INSERT INTO books (title, price) VALUES (%s, %s) RETURNING id, title, price",
            (book.title, book.price),
        ).fetchone()


@app.get("/books/{book_id}")
def get_book(book_id: int):
    with connect() as db:
        row = db.execute("SELECT id, title, price FROM books WHERE id = %s", (book_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "No book with that id")
    return row
