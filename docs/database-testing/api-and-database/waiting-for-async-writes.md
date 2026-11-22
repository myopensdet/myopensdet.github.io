---
title: "Wait for Late Database Writes Without sleep()"
description: "Some apps answer first and write later: background jobs, queues, events. Check those writes by asking again and again with a timeout, never with a fixed sleep. A small wait_for helper for pytest."
level: Intermediate
tags:
  - API
  - Database
  - pytest
nav_title: "Waiting for late writes"
order: 50
summary: "Ask again until the row is there, or fail after a timeout."
updated: "2026-11-22"
---

# Wait for Late Database Writes Without sleep()

Many apps answer the request first and finish the work afterwards: send the email, write the history, update the search index. A test that looks in the database straight after the answer finds nothing. A test that sleeps for two seconds is slow, and still fails on a busy day. The fix is **polling**: ask again and again until the row is there, or give up after a clear time limit.

!!! note "Before you start"
    Read [cleanup after API tests](cleanup-after-api-tests.md).

## What you will learn

- Why a read straight after the answer can miss the row
- A `wait_for` helper that polls with a timeout
- Why `time.sleep(2)` is the wrong fix
- What a good timeout failure says

## Why this matters at work

Late writes are behind most flaky API + database tests. They pass on your laptop and fail in the pipeline, or the other way round. Polling with a timeout makes them fast when the app is fast, and gives a clear message when the write never comes.

## The idea in plain words

!!! info "In plain words"
    You're waiting for a parcel. You don't sit at the door for exactly two hours. You look out every few minutes, and if it hasn't come by evening, you call the shop. `wait_for` looks every 0.2 seconds, and calls the shop after 5.

## Step by step

1. **See the miss.** The practice API writes an `order_created` event half a second after it answers. Read at once:

    ```python
    order = api.post("/orders", json={...}).json()
    print("read at once:", db.one("SELECT event FROM order_events WHERE order_id = %s", (order["id"],)))
    ```

    ```text
    read at once: None
    ```

2. **Poll instead.** `wait_for` in `helpers/clients.py`:

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/helpers/clients.py:80:92"
    ```

    It runs `check()`, returns the result as soon as it's not empty, and otherwise waits `every` seconds and tries again. `time.monotonic()` is used for the deadline because it never jumps when the computer's clock changes.

    ```text
    wait_for: {'event': 'order_created'} after 0.6 s
    ```

    0.6 seconds: as fast as the app, no slower.

3. **Write the test.** `tests/test_background_writes.py`:

    ```python
    --8<-- "modules/core_automation/api_and_database/templates/api_db_tests/tests/test_background_writes.py"
    ```

    ```text
    tests/test_background_writes.py::test_order_event_is_written PASSED      [100%]
    ============================== 1 passed in 0.68s ===============================
    ```

4. **Read the failure when the write never comes.** With an order id that has no event:

    ```text
    AssertionError: Waited 1 s for the order_created event for order -1, it never happened
    ```

    It names what was missing and how long the test waited. Compare that with a plain assert after one read, which only says:

    ```text
    E           AssertionError: assert None == {'event': 'order_created'}
    ```

    !!! success "Check: you should now be able to"
        Check a write the app makes after it answers, with a poll and a timeout instead of a sleep.

## When it goes wrong

- **It times out in the pipeline, and passes on your laptop.** The pipeline is slower. Ask the developers how long the job can take, and set the timeout above that. Don't just double it.
- **It times out every time.** The background job isn't running, or failed. Look in the app's log first.
- **It passes, but the value is wrong.** `wait_for` returns as soon as *something* is there. Check the value after it returns, as the template does.

## Common mistakes

!!! warning "Common mistakes"
    - **`time.sleep(2)` then read once.** Slow every run, and still flaky on a slow day.
    - **No timeout.** A missing write hangs the run until the pipeline kills it, with no message.
    - **Polling every 0.001 seconds.** Hundreds of queries a second against a shared database. 0.1 to 0.5 seconds is plenty.

!!! failure "If you see this error"
    **`AssertionError: Waited 5 s for the order_created event for order 412, it never happened`**
    Look for order 412 in the app's log. The background job either failed, or never started.

## Try it yourself

After `DELETE /orders/{id}`, the order's events disappear too (the table uses `ON DELETE CASCADE`). Write a check that waits for the order's event, deletes the order through the API, and then checks there are no events left.

??? success "Solution"
    ```python
    def test_events_go_with_the_order(api, db, place_order, customer, book):
        order = place_order(customer_id=customer["id"], book_id=book["id"], quantity=1)
        assert api.delete(f"/orders/{order['id']}").status_code == 204
        left = db.value("SELECT COUNT(*) FROM order_events WHERE order_id = %s", (order["id"],))
        assert left == 0
    ```

    `place_order` already waits for the event, so no `wait_for` is needed here. The delete happens in the same request, so there's nothing late to wait for afterwards.

## References

- [Python: time.monotonic](https://docs.python.org/3/library/time.html#time.monotonic)
- [FastAPI: Background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [Martin Fowler: Eradicating non-determinism in tests](https://martinfowler.com/articles/nonDeterminism.html)

Written for Python 3.13, pytest 9.2, psycopg 3.3 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
