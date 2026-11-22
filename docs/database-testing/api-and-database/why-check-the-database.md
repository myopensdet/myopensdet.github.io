---
title: "Why Check the Database After an API Call"
description: "An API answer is what the app says it did. The database shows what it really did. See the bugs only a database check can find: wrong values saved, missing side effects, duplicates and late writes."
level: Intermediate
tags:
  - API
  - Database
nav_title: "Why check the database"
order: 10
summary: "The answer is what the app says. The database is what it did."
updated: "2026-11-22"
---

# Why Check the Database After an API Call

An API test sends a request and checks the answer. That answer is the app describing what it did, and the app can be wrong about it. The database is where the work really lands. An API + database test checks both: **the answer, and the rows behind it.**

!!! note "Before you start"
    Read [API testing](../../api-testing/index.md) and [Database testing](../index.md). To follow along, start the practice bookshop API: the steps are in [Get something running](index.md#4-get-something-running).

## What you will learn

- What an API answer can't tell you
- Five kinds of bugs that only show up in the database
- Why "the answer and the row agree" isn't enough on its own

## Why this matters at work

Most API bugs that reach customers are not wrong status codes. They are wrong data: a price nobody checked, stock that didn't go down, a second account for the same person. These bugs pass every API test, and finance or support finds them weeks later.

## The idea in plain words

!!! info "In plain words"
    You ask a shop assistant to put a book aside for you. They say "Done!" That's the API answer. Whether the book is really on the shelf with your name on it is the database. A good tester walks over and looks at the shelf.

## Step by step

1. **Place an order and read the answer.** On the practice API, with one book priced 24.99:

    ```bash
    curl -s -X POST localhost:8090/orders -H 'content-type: application/json' \
      -d '{"customer_id":116,"book_id":67,"quantity":2}'
    ```

    ```text
    {"id":54,"customer_id":116,"book_id":67,"quantity":2,"unit_price":24.99,"total":49.98,"status":"new"} 201
    ```

    Status 201, the right total. An API test would pass here, and it should.

2. **Send one extra field.** A real client never sends a price. Someone testing the edges does:

    ```bash
    curl -s -X POST localhost:8090/orders -H 'content-type: application/json' \
      -d '{"customer_id":116,"book_id":67,"quantity":1,"unit_price":0.01}'
    ```

    ```text
    {"id":55,"customer_id":116,"book_id":67,"quantity":1,"unit_price":0.01,"total":0.01,"status":"new"} 201
    ```

    Still 201. The answer looks normal, and it's honest: the app did save 0.01.

3. **Look at the rows.**

    ```text
     id | quantity | unit_price | total | status
    ----+----------+------------+-------+--------
     54 |        2 |      24.99 | 49.98 | new
     55 |        1 |       0.01 |  0.01 | new
    ```

    The answer and the row agree, and both are wrong. That's the trap: the only way to see it is to compare the saved price with the book's price in the `books` table. It's the first of the two bugs planted in the practice API.

4. **Learn the five kinds of database-only bugs.**

    | The bug | What the API says | What the database shows |
    | --- | --- | --- |
    | Wrong value saved | 201 | a price, a total or a status that breaks a business rule |
    | Missing side effect | 201 | stock not reduced, no history row |
    | Partial write | 4xx or 500 | half an order saved after the error |
    | Duplicate | 201 | two customers for one email |
    | Late write that never comes | 201 | no event row, a second after the answer |

    !!! success "Check: you should now be able to"
        Explain why a correct API answer doesn't prove the data is right, and name the five kinds of bugs a database check finds.

## When it goes wrong

- **The API answer and the row disagree.** Report it straight away: either the answer or the save is wrong, and either way someone downstream reads the wrong one.
- **You can't get access to the database.** Ask for read access to a test database, never production. Until then, a `GET` after the `POST` checks a little more than the `POST` alone.
- **The row isn't there right after the call.** The app may write it later. See [waiting for late writes](waiting-for-async-writes.md).

## Common mistakes

!!! warning "Common mistakes"
    - **Checking that the row exists, and nothing else.** Check the values that matter: price, total, status, owner.
    - **Comparing the row with the answer only.** They come from the same code, so they can be wrong together. Compare with a value you know: the book's price, the stock before the call.
    - **Only testing what a real client sends.** Add fields, change types, leave fields out. The database shows what each one did.

!!! failure "If you see this error"
    **`psycopg.OperationalError: connection failed: connection to server at "127.0.0.1", port 5432 failed: could not receive data from server: Connection refused`**
    The test database isn't running, or not on that port. Run `docker compose ps` in the app's folder. If it shows nothing, `docker compose up -d --wait`.

## Try it yourself

On the practice API, create a customer, then send the same email again with capital letters. Is it refused? What's in the `customers` table?

??? success "Solution"
    `arshad@example.com` then `ARSHAD@example.com`: both answer 201, and the table has two rows. Email addresses are not case sensitive in practice, so this is the second planted bug: the same person can now sign up twice. The exact same email *is* refused with 409, because the database has a unique rule on it.

## References

- [OWASP: Mass Assignment Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Mass_Assignment_Cheat_Sheet.html)
- [OWASP API Security Top 10](https://owasp.org/API-Security/)

Written for Python 3.13, FastAPI 0.163 and PostgreSQL 17. Outputs captured November 2026. Links checked: November 2026.
