---
title: "Query and Path Parameters: ?page=2 and /booking/42"
description: "The difference between query parameters and path parameters, sending them safely with requests, how non-English text is encoded in URLs, and the boundary and negative cases to test for each."
level: Beginner
tags:
  - API
  - Test design
nav_title: "Query and path parameters"
order: 50
summary: "?page=2 and /booking/42: send them safely, and what to test for each."
updated: "2026-11-22"
---

# Query and Path Parameters: ?page=2 and /booking/42

There are two ways to put values in a URL. A **path parameter** is part of the path and usually names one thing: `/booking/42` is booking 42. A **query parameter** comes after `?` and usually filters, sorts or pages: `/booking?firstname=Test&page=2`. Both are inputs, and like every input, they deserve boundary and negative tests.

!!! note "Before you start"
    Read [How HTTP works](how-http-works.md) first.

## What you will learn

- When an API uses a path parameter, and when a query parameter
- How to send query parameters with `params=`
- How text like Bengali is encoded in a URL
- What to test for each kind

## Why this matters at work

Parameters are where APIs meet user input. An id of 0, a page of -1, a search for `%`, a name in Bengali: each one has broken real APIs. And an id in the path is where access bugs live: can you read booking 43 if it's not yours?

## The idea in plain words

!!! info "In plain words"
    The path is the address of a house: Street 7, flat 42. The query is a note for whoever opens the door: "only the post for Test, newest first".

## Step by step

1. **Run the example.**

    ```python
    --8<-- "modules/core_automation/api_testing/examples/params.py"
    ```

    ```bash
    python params.py
    ```

    ```text
    URL sent: https://httpbin.org/get?q=%E0%A6%AC%E0%A6%87&sort=price&page=2
    Server read: {'page': '2', 'q': 'বই', 'sort': 'price'}
    /booking/<id>: an id from the list -> 200
    /booking/<id>: 999999999 -> 404
    ```

2. **Send query parameters with `params=`.** `requests` builds `?q=...&sort=price&page=2` and encodes each value. The Bengali word "বই" became `%E0%A6%AC%E0%A6%87`: its UTF-8 bytes, written as `%` codes. The server decoded it back. Building the string by hand would break on spaces, `&`, `#` and non-English text.

3. **Put path parameters in the path.** `f"{BASE}/booking/{booking_id}"`. The example takes a real id from the booking list, so it doesn't depend on a fixed id that someone else might delete. A made-up id gives 404, which is right.

4. **Test path parameters.** For an id:

    | Case | Expect |
    | --- | --- |
    | An id that exists | 200 and the right data |
    | An id that doesn't exist | 404 |
    | 0, -1, a very big number | 404 or 400, never 500 |
    | Text, like `abc` | 400 or 404, never 500 |
    | Someone else's id | 403 or 404, never their data |

    The last row is the most important. It's the top API security risk, called broken object level authorization: [OWASP API1:2023](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/).

5. **Test query parameters.** For filters, sorting and paging:

    - **Filters:** one match, no matches, special characters (`%`, `'`, `&`), and Bengali text.
    - **Paging:** page 1, the last page, one past the last, 0 and -1, a page size of 0 and a huge one.
    - **Unknown parameters:** most APIs ignore them. Check that a typo like `?frstname=Test` doesn't silently return everything.

6. **Check the server read what you meant.** If the API echoes the filter, or the results, compare them with what you sent. A filter that's ignored looks exactly like a filter that matches everything.

    !!! success "Check: you should now be able to"
        Choose between a path and a query parameter, send both safely, and list the boundary and negative cases for each.

## When it goes wrong

- **A search with `&` or `#` returns the wrong results.** The query was built by hand. Use `params=`.
- **`404` for an id you just created.** Check the path: a missing slash, or the id has spaces or quotes from a copy. Print `response.url`.
- **A filter returns everything.** The parameter name is wrong, and the API ignores unknown names. Check the docs, and test the filter with a value that should match nothing.
- **Results come back in a different order each time.** Without a sort parameter, order isn't promised. Sort in the test, or ask the API to sort.

## Common mistakes

!!! warning "Common mistakes"
    - **Fixed ids like `/booking/1` in tests.** Create your own data, and use its id.
    - **Only testing ids that exist.** The interesting bugs are in the others.
    - **Never testing someone else's id.** That's the access check.

!!! failure "If you see this error"
    **`requests.exceptions.InvalidURL: Invalid URL ...: No host supplied`**
    The base URL is empty or wrong, often a missing environment variable. Print the URL before sending, and check the setting.

## Try it yourself

Call `https://httpbin.org/get` with `params={"name": "Test & Co", "tag": ["a", "b"]}`. Look at `response.url` and the `args` in the answer. What did `requests` do with the `&` and the list?

??? success "Solution"
    The URL ends with `?name=Test+%26+Co&tag=a&tag=b`. The `&` inside the value became `%26` (and spaces became `+`), so it isn't read as a new parameter. The list became the same name twice, `tag=a&tag=b`, which is how many APIs read lists in a query. The server read it all back correctly: `{'name': 'Test & Co', 'tag': ['a', 'b']}`.

## Quick check

1. When does an API use a path parameter?

    ??? question "Answer"
        Usually to name one thing, like `/booking/42`.

2. Why use `params=` instead of building the query yourself?

    ??? question "Answer"
        It encodes each value, so spaces, `&`, `#` and non-English text arrive correctly.

3. What should happen when you ask for another user's booking?

    ??? question "Answer"
        403 or 404. Never their data.

## References

- [Requests: Passing parameters in URLs](https://requests.readthedocs.io/en/latest/user/quickstart/#passing-parameters-in-urls)
- [MDN: URI query](https://developer.mozilla.org/en-US/docs/Web/URI/Reference/Query)
- [OWASP API1:2023 Broken Object Level Authorization](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/)

Written for Python 3.13 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
