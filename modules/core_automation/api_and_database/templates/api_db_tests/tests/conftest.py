# Template from myOpenSDET: https://myopensdet.github.io/
"""Fixtures: the API, the database, and data that cleans itself up.

Settings come from the environment:
    API_URL        where the API is, for example http://127.0.0.1:8090
    DATABASE_URL   the database behind it (a test database, never production)
"""

import uuid

import pytest
from helpers.clients import Api, Cleanup, Db, check_status, setting, wait_for


@pytest.fixture(scope="session")
def api():
    try:
        return Api(setting("API_URL"))
    except LookupError as error:
        pytest.skip(str(error))


@pytest.fixture(scope="session")
def db():
    try:
        database = Db(setting("DATABASE_URL"))
    except LookupError as error:
        pytest.skip(str(error))
    yield database
    database.close()


@pytest.fixture
def cleanup(db):
    tracker = Cleanup(db)
    yield tracker
    tracker.run()  # runs even when the test failed


@pytest.fixture
def unique():
    """A short random tag, so test data never clashes with other runs or people."""
    return uuid.uuid4().hex[:8]


@pytest.fixture
def customer(api, cleanup, unique):
    """A customer made through the API, the way a real user would."""
    response = api.post(
        "/customers", json={"email": f"test.{unique}@example.com", "full_name": "Api Test"}
    )
    check_status(response, 201)
    body = response.json()
    cleanup.add("customers", body["id"])
    return body


@pytest.fixture
def book(db, cleanup, unique):
    """A book put straight into the database: faster than the API, and needs no admin login."""
    row = db.one(
        "INSERT INTO books (title, price, stock) VALUES (%s, %s, %s) RETURNING id, price, stock",
        (f"Test Book {unique}", 24.99, 10),
    )
    cleanup.add("books", row["id"])
    return row


@pytest.fixture
def place_order(api, db, cleanup):
    """Place an order through the API and wait until the app has finished with it.

    The app writes an order_created event half a second after it answers. Deleting the
    order before that makes the app crash in the background, so wait for the event first.
    """

    def place(**body):
        response = api.post("/orders", json=body)
        check_status(response, 201)
        order = response.json()
        cleanup.add("orders", order["id"])
        wait_for(
            lambda: db.one("SELECT 1 FROM order_events WHERE order_id = %s", (order["id"],)),
            what=f"the app to finish order {order['id']}",
        )
        return order

    return place
