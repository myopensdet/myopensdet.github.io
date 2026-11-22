# Template from myOpenSDET: https://myopensdet.github.io/
"""Checks of the book API, and of what it saves in the database."""

from conftest import API_URL


def test_health_says_the_database_is_up(api):
    response = api.get(f"{API_URL}/health", timeout=5)
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "up"}


def test_a_new_book_can_be_read_back(api):
    new_book = {"title": "Docker Basics", "price": "19.99"}
    created = api.post(f"{API_URL}/books", json=new_book, timeout=5)
    assert created.status_code == 201
    book = created.json()

    read = api.get(f"{API_URL}/books/{book['id']}", timeout=5)
    assert read.status_code == 200
    assert read.json() == book


def test_a_new_book_is_saved_in_the_database(api, db):
    new_book = {"title": "Compose in Practice", "price": "24.50"}
    book = api.post(f"{API_URL}/books", json=new_book, timeout=5)
    row = db.execute("SELECT title, price::text FROM books WHERE id = %s", (book.json()["id"],))
    assert row.fetchone() == ("Compose in Practice", "24.50")


def test_a_price_of_zero_is_refused(api):
    response = api.post(f"{API_URL}/books", json={"title": "Free Book", "price": "0"}, timeout=5)
    assert response.status_code == 422


def test_an_unknown_book_is_not_found(api):
    response = api.get(f"{API_URL}/books/999999", timeout=5)
    assert response.status_code == 404
