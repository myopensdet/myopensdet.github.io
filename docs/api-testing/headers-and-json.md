---
title: "Headers and JSON: What Goes With Every Request, and the Two Ways to Send Data"
description: "HTTP headers an API tester uses every day (Accept, Content-Type, Authorization, custom headers), how requests sends JSON with json= and form data with data=, and how to check response headers and JSON bodies."
level: Beginner
tags:
  - API
  - Python
nav_title: "Headers and JSON"
order: 40
summary: "Accept, Content-Type and custom headers, and json= versus data=."
updated: "2026-11-22"
---

# Headers and JSON: What Goes With Every Request, and the Two Ways to Send Data

**Headers** are the notes on the envelope: what kind of answer you want (`Accept`), what kind of body you're sending (`Content-Type`), who you are (`Authorization`), and anything else the API asks for. The **body** is the data, usually JSON. In `requests`, `json=` sends JSON and sets the right header for you. `data=` sends a form. Mixing them up is one of the most common reasons a request "works in Postman but not in Python".

!!! note "Before you start"
    Read [How HTTP works](how-http-works.md), and [JSON](../programming-for-testers/json.md) if JSON is new to you.

## What you will learn

- The headers you'll set and check most
- How to send custom headers
- The difference between `json=` and `data=`
- How to check response headers and JSON bodies

## Why this matters at work

Wrong headers cause confusing failures: a 415 because `Content-Type` is wrong, HTML instead of JSON because `Accept` is missing, a 400 because the body was sent as a form. And response headers are worth testing too: the content type, caching rules, and security headers.

## The idea in plain words

!!! info "In plain words"
    Headers are the labels on a parcel: "fragile", "this way up", "from: ...". The body is what's inside. The right labels make sure the parcel is handled right.

## Step by step

1. **Run the example.**

    ```python
    --8<-- "modules/core_automation/api_testing/examples/headers_and_json.py"
    ```

    ```bash
    python headers_and_json.py
    ```

    ```text
    The server saw: {'Accept': 'application/json', 'X-Test-Run': 'nightly-42', 'User-Agent': 'python-requests/2.34.2'}
    json=  -> application/json {'items': 2, 'name': 'আরশাদ'}
    data=  -> application/x-www-form-urlencoded {'items': '2', 'name': 'Pen'}
    Response type: application/json
    Title: Sample Slide Show
    ```

2. **Send headers as a dictionary.** `headers={"Accept": "application/json", "X-Test-Run": "nightly-42"}`. The server saw both, plus `User-Agent`, which `requests` adds. Custom headers like `X-Test-Run` help find your test's requests in the server's logs.

3. **Use `json=` for JSON APIs.** It turns the dictionary into JSON text and sets `Content-Type: application/json`. Look at the output: the numbers stay numbers (`'items': 2`), and the Bengali name arrives as it is.

4. **Know what `data=` does.** It sends a form, `application/x-www-form-urlencoded`, like an HTML form. Everything becomes text: `'items': '2'`. A JSON API that gets a form usually answers 400 or 415. Use `data=` only when the API asks for a form, as some login endpoints do.

5. **Check the response headers.** `response.headers["Content-Type"]` should say JSON when you expect JSON. Header names don't care about capital letters in HTTP, and `requests` lets you read them either way: `response.headers["content-type"]` works too.

6. **Check the JSON body.** `response.json()` gives a dictionary or a list. Check the values that matter, and the shape of the whole body with a [schema](schema-validation.md). For a list, check its length and one or two items, not only that it isn't empty.

    !!! success "Check: you should now be able to"
        Send custom headers, choose between `json=` and `data=`, and check a response's content type and body.

## When it goes wrong

- **`415 Unsupported Media Type`.** The server doesn't accept that `Content-Type`. You probably used `data=` for a JSON API. Switch to `json=`.
- **The body arrives empty on the server.** You set `Content-Type: application/json` by hand, but sent a dictionary with `data=`. Let `json=` do both.
- **The answer is HTML, not JSON.** Send `Accept: application/json`. Some APIs return HTML error pages to browsers and JSON to clients that ask for it.
- **A header you sent never arrives.** A proxy may remove it. httpbin's proxy drops some headers, like `X-Request-Id`. Check with the team which headers pass through.

## Common mistakes

!!! warning "Common mistakes"
    - **`data=json.dumps(body)` without a Content-Type.** Use `json=body`.
    - **Logging every header.** `Authorization` and `Cookie` hold secrets. Hide them, as the [API client](api-client-class.md) does.
    - **Checking only one field of a big body.** Add a schema check for the rest.

!!! failure "If you see this error"
    **`TypeError: Object of type date is not JSON serializable`**
    You passed a `date` in `json=`. JSON has no date type. Send `value.isoformat()`, a string like `"2026-12-01"`.

## Try it yourself

Send `{"price": 4.25, "tags": ["paper"]}` to `https://httpbin.org/anything`, once with `json=` and once with `data=`. Print `response.json()["json"]` and `response.json()["form"]` each time. What happened to the list?

??? success "Solution"
    With `json=`, the server gets `{'price': 4.25, 'tags': ['paper']}`: a number and a list. With `data=`, the form has `{'price': '4.25', 'tags': 'paper'}`: everything is text, and the list became one value. Forms can't carry nested data. That's why JSON APIs use JSON.

## Quick check

1. What does `json=` set for you?

    ??? question "Answer"
        The JSON text in the body, and the header `Content-Type: application/json`.

2. When would you use `data=`?

    ??? question "Answer"
        When the API expects a form, `application/x-www-form-urlencoded`, like some login endpoints.

3. Which headers must never appear in logs?

    ??? question "Answer"
        Ones holding secrets: `Authorization`, `Cookie`, and API key headers.

## References

- [MDN: HTTP headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers)
- [Requests: Custom headers](https://requests.readthedocs.io/en/latest/user/quickstart/#custom-headers)
- [MDN: Sending form data](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Forms/Sending_and_retrieving_form_data)

Written for Python 3.13 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
