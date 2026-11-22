---
title: "Debugging Toolkit for Testers: Find the Real Cause of a Failure, Step by Step"
description: "How to debug a failing test at work, step by step: read the failure, run one test alone, rerun only failures, show local variables and logs, stop in the debugger with pytest --pdb, look at the raw request with curl -v and browser developer tools, and write the cause in one sentence. A practice project with three planted bugs and a checklist."
level: Beginner
tags:
  - Debugging
  - pytest
  - Templates
nav_title: "Debugging toolkit"
order: 60
summary: "Read the failure, run it alone, logs, the debugger, curl -v and DevTools."
updated: "2026-11-22"
code: "infrastructure/debugging_toolkit"
---

# Debugging Toolkit for Testers: Find the Real Cause of a Failure, Step by Step

A red test is a question, not an answer. "Test failed" helps nobody; "the cart keeps items from the previous test, because every cart shares one list" gets fixed the same day. This guide is the routine experienced testers follow, on a small practice project with three bugs hidden in it.

!!! example "The situation"
    **Your lead:** "Three cart tests went red last night. Can you find out why before stand-up?"

## Step 1: Get the practice project

You need **Python 3.13**. If you don't have it, follow [environment setup](../../getting-started/environment-setup/index.md) first.

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/infrastructure/debugging_toolkit/templates). Then open the `debug_practice` folder in VS Code.
2. In the VS Code terminal, make a virtual environment and install pytest:

    === "macOS / Linux"

        ```bash
        python3.13 -m venv .venv
        source .venv/bin/activate
        python -m pip install -r requirements.txt
        ```

    === "Windows"

        ```powershell
        py -3.13 -m venv .venv
        .venv\Scripts\Activate.ps1
        python -m pip install -r requirements.txt
        ```

The project is a tiny shop cart: `shop/cart.py`, `shop/discounts.py`, and five tests in `tests/test_cart.py`. Don't read the code yet: debug the way you would on a project you don't know.

## Step 2: Read the failure from the bottom up

```bash
python -m pytest
```

The end of the output is the place to start:

```text
FAILED tests/test_cart.py::test_two_cheap_items - assert 24.8 == 0.3
FAILED tests/test_cart.py::test_discount_code_typed_in_small_letters - Assert...
FAILED tests/test_cart.py::test_unknown_discount_code_gives_no_discount - Key...
========================= 3 failed, 2 passed in 0.04s ==========================
```

Then scroll up to each failure. A failure has three parts:

```text
    def percent_off(code: str | None) -> int:
        if code is None:
            return 0
        log.debug("looking up discount code %r", code)
>       return CODES[code.upper()]
               ^^^^^^^^^^^^^^^^^^^
E       KeyError: 'SPRING'

shop/discounts.py:15: KeyError
```

| Part | Tells you |
| --- | --- |
| The `>` line | The exact line that broke |
| The `E` lines | **What** went wrong: here, `'SPRING'` isn't in the list of codes |
| The last `file:line` | **Where**: `shop/discounts.py`, line 15. Above it, pytest shows the path from your test down to there |

Read each failure and write one line for it before doing anything else:

1. `test_two_cheap_items`: a pen and a pencil cost **24.8**? Expected 0.3.
2. `test_discount_code_typed_in_small_letters`: one book of 50.00 with 10% off costs **67.32**? Expected 45.
3. `test_unknown_discount_code_gives_no_discount`: an unknown code **crashes** with `KeyError`.

Failures 1 and 2 have numbers that are much too big. That's a clue: something is being added that shouldn't be.

## Step 3: Run one test alone

```bash
python -m pytest "tests/test_cart.py::test_two_cheap_items"
```

```text
E       assert 0.30000000000000004 == 0.3
============================== 1 failed in 0.03s ===============================
```

```bash
python -m pytest -k small_letters
```

```text
======================= 1 passed, 4 deselected in 0.01s ========================
```

This is the most useful trick in debugging:

| Alone, the test... | Means |
| --- | --- |
| Fails the same way | The problem is in this test, or the code it calls |
| **Passes, or fails differently** | **Something is shared between tests**: data, a list, a file, a database row, the order they run in |

Both tests behave differently alone. So the 24.8 and the 67.32 come from **other tests' items**. One cause, two failures. (And alone, `test_two_cheap_items` shows a second, different problem: `0.30000000000000004`. Keep that for later.)

## Step 4: Rerun only what failed, and stop early

While you investigate, don't run everything every time:

| Command | Does |
| --- | --- |
| `pytest --lf` | Runs only the tests that **failed last time** |
| `pytest -x` | **Stops at the first** failure |
| `pytest --lf -x` | Both: the fastest loop while you fix |
| `pytest -k discount` | Only tests with "discount" in the name |

```text
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
========================= 1 failed, 2 passed in 0.01s ==========================
```

## Step 5: See more: logs and local variables

**Logs.** Most apps write debug messages that are hidden by default. Show them while the tests run:

```bash
python -m pytest --log-cli-level=DEBUG
```

```text
DEBUG    shop.cart:cart.py:21 subtotal=0 off=0%
DEBUG    shop.cart:cart.py:21 subtotal=24.5 off=0%
DEBUG    shop.cart:cart.py:21 subtotal=24.8 off=0%
DEBUG    shop.discounts:discounts.py:14 looking up discount code 'welcome10'
DEBUG    shop.cart:cart.py:21 subtotal=74.8 off=10%
```

Each test starts with a new, empty cart, so each subtotal should start fresh. Instead it **grows**: 24.5, then 24.8 (24.5 + 0.10 + 0.20), then 74.8 (+ 50). The items carry over from test to test.

**Local variables.** `-l` prints the variables of the failing test:

```bash
python -m pytest -l
```

```text
E       AssertionError: assert 67.32 == 45.0
E        +  where 67.32 = total('welcome10')

cart       = <shop.cart.Cart object at 0x1096009d0>
```

Only `<Cart object>`: not enough to see inside. Time for the debugger.

!!! warning "`-l` prints everything, secrets too"
    Local variables can hold tokens and passwords. Don't paste `-l` output into tickets without reading it, and never turn it on in a shared pipeline.

## Step 6: Stop at the failure and look around

`--pdb` stops at the failure and lets you type Python to look at anything. No code changes needed:

```bash
python -m pytest --pdb -x -k "not two_cheap"
```

```text
>>>>>>>>>>>>>>>>>> PDB post_mortem (IO-capturing turned off) >>>>>>>>>>>>>>>>>>>
> .../debug_practice/tests/test_cart.py(27)test_discount_code_typed_in_small_letters()
-> assert cart.total("welcome10") == 45.00
(Pdb) p cart.items
[('Python book', 24.5, 1), ('Python book', 50.0, 1)]
(Pdb) q
```

**Found it.** The new cart already holds the 24.50 book from `test_one_book`. Now read the code with that in mind:

```python
class Cart:
    def __init__(self, items=[]):
        self.items = items
```

`items=[]` is made **once**, when Python reads the file, and every `Cart()` gets the **same** list. A classic Python bug. The fix: `items=None`, then `self.items = list(items or [])`.

The debugger commands you need:

| Type | Does |
| --- | --- |
| `p name` | Print a value |
| `pp name` | Print it nicely (long lists, dicts) |
| `l` | Show the code around this line |
| `u`, `d` | Go up to the caller, back down |
| `q` | Quit |

To stop **before** something goes wrong, put `breakpoint()` on a line in the test and run `python -m pytest -s`. In VS Code, a red dot next to the line number and **Run → Start Debugging** does the same with a mouse.

## Step 7: One fix at a time, then run everything

With the shared list fixed, run all the tests again:

```text
FAILED tests/test_cart.py::test_two_cheap_items - assert 0.30000000000000004 ...
FAILED tests/test_cart.py::test_unknown_discount_code_gives_no_discount - Key...
========================= 2 failed, 3 passed in 0.02s ==========================
```

One bug was hiding another. The two that remain:

| Failure | Cause | Bug or question? |
| --- | --- | --- |
| `0.30000000000000004 == 0.3` | Computers store `0.1` and `0.2` with tiny errors. Money in `float` adds them up | **Bug.** Money should be `Decimal`, or rounded to cents. In tests, compare floats with `pytest.approx` |
| `KeyError: 'SPRING'` | An unknown code crashes the cart | **Ask first:** should an unknown code give no discount, or a message to the user? Then it's a bug either way: a crash is never right |

**Write the cause in one sentence** for each, before you report or fix. If you can't, you haven't found it yet.

## Step 8: Look at the real request: curl -v and DevTools

For API and UI tests, the bug is often in what was sent or received. Look at it raw.

**`curl -v`** shows the request (`>` lines) and the answer (`<` lines):

```bash
curl -v http://127.0.0.1:8792/api/orders/7 -H "Accept: application/json"
```

```text
* Connected to 127.0.0.1 (127.0.0.1) port 8792
> GET /api/orders/7 HTTP/1.1
> Host: 127.0.0.1:8792
> User-Agent: curl/8.7.1
> Accept: application/json
>
< HTTP/1.0 404 File not found
< Server: SimpleHTTP/0.6 Python/3.13.18
< Content-Type: text/html;charset=utf-8
```

Asked for JSON, got an HTML 404 page from a plain file server: the address points at the wrong server. You can see that in one look.

**Browser developer tools** (F12, or right-click → Inspect) for UI problems:

| Tab | Look for |
| --- | --- |
| **Console** | Red errors from the page's scripts; "blocked by CORS policy" |
| **Network** | Every request the page made: status, time, request and answer. Click one, then **Headers**, **Payload**, **Response**. Filter by "Fetch/XHR" for API calls |
| **Network → Preserve log** | Keeps requests when the page reloads or moves on (logins, redirects) |
| **Application** | Cookies and stored data: is the user really logged in? |

A UI test that "clicks Save and nothing happens" usually shows a red 500 in the Network tab. Then it's an API bug, and you can [test the API directly](../../case-studies/automate-api-tests/index.md).

Server-side, follow the request in the logs: see [Linux and shell, step 6](../linux/index.md#step-6-follow-one-request-across-logs).

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| The test passes alone, fails with the others | Shared state: a list, a file, a database row, an environment variable | Each test makes its own data. Look for module-level variables and default arguments |
| It fails on the pipeline, passes on your computer | A different environment: time zone, data, versions, speed, missing secrets | Compare versions and settings. Run the pipeline's command locally, in [Docker](../docker/index.md) if you can |
| It fails sometimes, passes sometimes | A flaky test: timing, order or shared data | See [flaky tests](../../automation-testing/flaky-tests/index.md). Don't just add a retry |
| `--pdb` shows nothing, the test just hangs | The debugger waits for typing, but output is captured | Use `-s` with `breakpoint()`. Never leave `breakpoint()` in a pushed test |
| `ERROR` instead of `FAILED` | The setup (a fixture) broke, not the test | Read the error in the fixture: often a missing setting or a server that isn't running |
| `ModuleNotFoundError: No module named 'shop'` | The test file was run with plain `python tests/test_cart.py` | Run tests with `python -m pytest` from the project folder, the one with `pytest.ini` |

### The checklist

```markdown
--8<-- "modules/infrastructure/debugging_toolkit/templates/debugging_checklist.md"
```

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/infrastructure/debugging_toolkit/templates).

=== "shop/cart.py"

    ```python
    --8<-- "modules/infrastructure/debugging_toolkit/templates/debug_practice/shop/cart.py"
    ```

=== "tests/test_cart.py"

    ```python
    --8<-- "modules/infrastructure/debugging_toolkit/templates/debug_practice/tests/test_cart.py"
    ```

## References

- [pytest: How to handle test failures (--pdb, -x, --lf)](https://docs.pytest.org/en/stable/how-to/failures.html)
- [pytest: How to manage logging](https://docs.pytest.org/en/stable/how-to/logging.html)
- [Python: pdb, the debugger](https://docs.python.org/3/library/pdb.html)
- [Python: floating point arithmetic](https://docs.python.org/3/tutorial/floatingpoint.html)
- [Chrome DevTools: Network panel](https://developer.chrome.com/docs/devtools/network)
- [VS Code: Python debugging](https://code.visualstudio.com/docs/python/debugging)

Written for Python 3.13 and pytest 9. Outputs captured November 2026. Links checked: November 2026.
