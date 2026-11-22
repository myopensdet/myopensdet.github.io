---
title: "How HTTP Works: A Request, a Response, and What's in Each"
description: "The parts of an HTTP request and response every API tester needs: method, URL, headers, body, status code and reason, shown with one real request from Python's requests library."
level: Beginner
tags:
  - API
  - Networking
nav_title: "How HTTP works"
order: 10
summary: "A request, a response, and what's in each, seen from Python."
updated: "2026-11-22"
---

# How HTTP Works: A Request, a Response, and What's in Each

Every API call is a conversation in two parts. The **request** says what you want: a method like GET, a URL, some headers, and sometimes a body. The **response** answers: a status code, headers, and usually a body. Once you can name those parts, every API test reads the same way: send a request, then check the parts of the response.

!!! note "Before you start"
    Install `requests` in a virtual environment. Run the example from this topic's `examples` folder.

## What you will learn

- The parts of an HTTP request and response
- How to send a request with `requests` and look at each part
- What "stateless" means, and why it matters for tests
- Where HTTPS fits in

## Why this matters at work

When an API test fails, the first question is "which part was wrong?" The status, a header, or the body? Testers who can name the parts read failures in seconds, and write bug reports developers can act on.

## The idea in plain words

!!! info "In plain words"
    A request is a letter: an envelope with an address and a few notes on it (the headers), and maybe a page inside (the body). The response is the reply letter, with a stamp on the outside saying how it went (the status code).

## Step by step

1. **Send one request.**

    ```python
    --8<-- "modules/core_automation/api_testing/examples/http_basics.py"
    ```

    ```bash
    python http_basics.py
    ```

    ```text
    Request:  GET https://httpbin.org/get?page=2
    Status:   200 OK
    Type:     application/json
    OK?       True
    Body has: ['args', 'headers', 'method', 'origin', 'url']
    args:     {'page': '2'}
    ```

    [httpbin.org](https://httpbin.org/) is a public service that answers with details of the request you sent. It's made for learning and testing HTTP.

2. **Read the request.** The **method** (`GET`) says what kind of action. The **URL** says where: the scheme (`https`), the host (`httpbin.org`), the path (`/get`) and the query (`?page=2`). `requests` built the query from `params={"page": 2}`.

3. **Read the response.** The **status code** `200` and its **reason** `OK` say how it went. The **headers** describe the answer: `Content-Type: application/json` says the body is JSON. The **body** is the data itself, and `response.json()` turns it into a dictionary. `response.ok` is `True` for any status below 400.

4. **Know that HTTP is stateless.** Each request stands alone. The server doesn't remember your last one, unless you send something that reminds it, like a token or a cookie. That's why login tokens go in a header on every request, and why tests can run in any order, if each one sends everything it needs.

5. **Know where HTTPS fits.** HTTPS is the same conversation, encrypted on the way. `requests` checks the server's certificate by default. Never turn that off with `verify=False` in tests that run against real environments. If a test environment has a self-signed certificate, ask for its certificate file and pass it with `verify="path/to/cert.pem"`.

    !!! success "Check: you should now be able to"
        Name the parts of a request and a response, send a request with `requests`, and print each part.

## When it goes wrong

- **`requests.exceptions.ConnectionError`.** No answer at all: wrong host, no internet, a proxy, or the server is down. Try the URL in a browser, or with `curl`, to see if it's your code or the network.
- **`requests.exceptions.ReadTimeout`.** The server didn't answer in time. Always pass `timeout=`. Without it, a stuck server makes the test wait forever.
- **`requests.exceptions.JSONDecodeError`.** The body isn't JSON. Print `response.status_code` and `response.text[:200]`. Error pages are often HTML.
- **`SSLError: certificate verify failed`.** The certificate isn't trusted. On a company network, a proxy may replace certificates. Ask for the company's certificate bundle, and pass it with `verify=`.

## Common mistakes

!!! warning "Common mistakes"
    - **No `timeout`.** Every request in a test needs one.
    - **Building query strings by hand**, like `"?q=" + text`. Use `params=`, which encodes the text for you.
    - **`verify=False` to make an error go away.** Fix the certificate instead.

!!! failure "If you see this error"
    **`requests.exceptions.MissingSchema: Invalid URL 'httpbin.org/get': No scheme supplied. Perhaps you meant https://httpbin.org/get?`**
    The URL needs `https://` (or `http://`) at the start. Usually the base URL in a setting is missing it.

## Try it yourself

Change the example to ask for `https://httpbin.org/get` with two parameters, `name=Test` and `page=3`. Which line of the output changes, and how?

??? success "Solution"
    Use `params={"name": "Test", "page": 3}`. The request line becomes `GET https://httpbin.org/get?name=Test&page=3`, and `args` shows both values, as text: `{'name': 'Test', 'page': '3'}`. Everything in a URL is text, even numbers.

## References

- [MDN: An overview of HTTP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview)
- [Requests: Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [Requests: Timeouts](https://requests.readthedocs.io/en/latest/user/quickstart/#timeouts)
- [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110)

Written for Python 3.13 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
