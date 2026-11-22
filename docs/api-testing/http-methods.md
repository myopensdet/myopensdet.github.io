---
title: "GET, POST, PUT, PATCH and DELETE: The Five Methods on One Booking"
description: "What GET, POST, PUT, PATCH and DELETE do, the difference between PUT and PATCH, which methods are safe and idempotent, and a full create-read-update-delete run against a real booking API."
level: Beginner
tags:
  - API
  - Python
nav_title: "GET, POST, PUT, PATCH, DELETE"
order: 20
summary: "The five methods on one booking, and the difference between PUT and PATCH."
updated: "2026-11-22"
---

# GET, POST, PUT, PATCH and DELETE: The Five Methods on One Booking

Five HTTP methods do almost all the work in a REST API. **GET** reads, **POST** creates, **PUT** replaces, **PATCH** changes part of something, and **DELETE** removes it. Together they're often called CRUD: create, read, update, delete. This lesson runs all five on one real booking, and shows what to test for each.

!!! note "Before you start"
    Read [How HTTP works](how-http-works.md) first. The example needs Restful-booker's public demo login: `export BOOKER_USERNAME=admin BOOKER_PASSWORD=password123`.

## What you will learn

- What each method does, and what it sends
- The difference between PUT and PATCH
- What "safe" and "idempotent" mean, and why testers care
- What to check after each method

## Why this matters at work

Most API bugs hide in updates and deletes: a PATCH that wipes the fields you didn't send, a DELETE that answers "done" but leaves the data, a PUT that works without login. Knowing what each method *should* do tells you what to check.

## The idea in plain words

!!! info "In plain words"
    Think of a library card file. GET is reading a card. POST is adding a new card. PUT is throwing a card away and writing a new one in its place. PATCH is crossing out one line and writing the new value. DELETE is taking the card out.

## Step by step

1. **Run the tour.**

    ```python
    --8<-- "modules/core_automation/api_testing/examples/methods_tour.py"
    ```

    ```bash
    python methods_tour.py
    ```

    ```text
    POST    200 new booking id: 1226
    GET     200 Test 120
    PUT     200 totalprice is now 150
    PATCH   200 Late checkout 150
    DELETE  201 Created
    GET     404 Not Found
    ```

    Your booking id will be different.

2. **POST creates.** It sends the new booking as JSON in the body (`json=booking`), and the answer has the new id. Check: the id is there, and the saved data equals what you sent.

3. **GET reads.** No body, just the id in the path. Check: the data is what was saved. GET must never change anything.

4. **PUT replaces.** It sends the *whole* booking. A field left out may be cleared or refused. Check: GET afterwards shows exactly what you sent.

5. **PATCH changes part.** It sends only `additionalneeds`. Look at the output: the total is still 150 from the PUT. Check: the field you sent changed, and every other field stayed the same. That second check is the one people forget.

6. **DELETE removes.** Check: the answer says it worked, and a GET afterwards gives 404. Don't trust the DELETE answer alone. Restful-booker answers `201 Created` to a delete, which is a wrong status code. The data is gone, though, so the GET is what proves it.

7. **Know safe and idempotent.**

    | Method | Safe (changes nothing) | Idempotent (same result if repeated) |
    | --- | --- | --- |
    | GET | Yes | Yes |
    | POST | No | No: two POSTs make two bookings |
    | PUT | No | Yes: the same PUT twice gives the same booking |
    | PATCH | No | Not always |
    | DELETE | No | Yes: after the first, it's already gone |

    Idempotency matters when a request is retried after a timeout. Retrying a PUT is harmless. Retrying a POST can create a duplicate, or charge a card twice. That's worth a test.

    !!! success "Check: you should now be able to"
        Say what each method does, explain PUT versus PATCH, and name the check after each one.

## When it goes wrong

- **`405 Method Not Allowed`.** The path doesn't accept that method. Check the docs: maybe it's `PATCH` not `PUT`, or the path is different.
- **`403 Forbidden` on PUT, PATCH or DELETE.** The login is missing or wrong. Restful-booker wants `Cookie: token=...`. See [authentication](authentication.md).
- **PATCH clears fields you didn't send.** That's a bug: the API is treating PATCH like PUT. Report it with the before and after GET.
- **`500` after POST with a missing field.** The API should answer 400 and say which field is missing. Restful-booker answers 500. Report it as a bug.

## Common mistakes

!!! warning "Common mistakes"
    - **Not checking the other fields after PATCH.** That's where PATCH bugs live.
    - **Trusting the DELETE answer.** GET afterwards, and expect 404.
    - **Using GET to change things.** If an API does, that's a design bug worth reporting.

!!! failure "If you see this error"
    **`KeyError: 'bookingid'` right after POST**
    The POST failed, so the body has no id. Print `response.status_code` and `response.text` before reading the body. Better: check the status first, as the [API client](api-client-class.md) lesson's `check_status` does.

## Try it yourself

Change the tour so the PATCH sends `{"totalprice": 99}` instead. What should the next GET show for `additionalneeds`, and why? Add a GET after the PATCH to check.

??? success "Solution"
    ```python
    patched = requests.patch(f"{BASE}/booking/{booking_id}", json={"totalprice": 99}, headers=auth, timeout=15)
    after = requests.get(f"{BASE}/booking/{booking_id}", headers=JSON, timeout=15).json()
    print(after["totalprice"], after["additionalneeds"])
    ```

    It should print `99 Breakfast`: PATCH changes only what you send, so `additionalneeds` keeps its value from the POST.

## Quick check

1. What is the difference between PUT and PATCH?

    ??? question "Answer"
        PUT replaces the whole thing. PATCH changes only the fields you send.

2. How do you check that a DELETE really worked?

    ??? question "Answer"
        GET the same id afterwards, and expect 404.

3. Why is retrying a POST risky?

    ??? question "Answer"
        POST isn't idempotent. A retry can create a second booking or a second payment.

## References

- [MDN: HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods)
- [RFC 9110: Methods, safe and idempotent](https://www.rfc-editor.org/rfc/rfc9110#name-methods)
- [Restful-booker API docs](https://restful-booker.herokuapp.com/apidoc/index.html)

Written for Python 3.13 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
