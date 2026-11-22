---
title: "Everyday Tools for Testers: From a Copied Request to a Test, Step by Step"
description: "The everyday tools of a tester at work, step by step: copy a request from the browser, Postman or Bruno as curl, try it in the terminal, turn it into a pytest test with a ready script, keep tokens out of the code, and debug the test in VS Code with breakpoints. Real outputs and ready VS Code settings."
level: Beginner
tags:
  - Tools
  - API
  - Templates
nav_title: "Everyday tools"
order: 40
group: "Your toolkit"
summary: "Copy a request as curl, turn it into a pytest test, debug it in VS Code."
updated: "2026-11-22"
---

# Everyday Tools for Testers: From a Copied Request to a Test, Step by Step

Most API tests start the same way: someone clicks through the app, finds the one request that matters, and says "can we have a test for this?". This guide takes that request from the browser (or Postman, or Bruno) to a pytest test that runs every day, without typing the request by hand, and without pasting anyone's token into the code.

!!! example "The situation"
    **Your lead:** "Adding a product works in the app. Can you turn that into an automated check before the release?"

## Step 1: Get the kit

You need **Python 3.13** and an editor. [VS Code](https://code.visualstudio.com/) is free and used here. If you don't have Python, follow [environment setup](../../start-here/environment-setup/index.md) first.

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/arshaduzzaman-sm/myopensdet/tree/main/modules/infrastructure/everyday_tools/templates). Then open the `everyday_kit` folder in VS Code (**File → Open Folder**).
2. Open the terminal in VS Code (**Terminal → New Terminal**) and install the two packages:

    ```bash
    python -m pip install -r requirements.txt
    ```

The kit has `curl_to_pytest.py` (the converter), an example copied request, and a `vscode` folder with ready settings.

## Step 2: Copy the request as curl

**curl** is a command that sends one request from the terminal. Every tool can give you the request it sent as a curl command, so curl is how requests travel between tools:

| From | How |
| --- | --- |
| **The browser** | Open the developer tools (F12), **Network** tab. Do the action in the app. Right-click the request → **Copy** → **Copy as cURL (bash)** |
| **Postman** | Open the request, click the **Code** icon (`</>`) on the right, choose **cURL** |
| **Bruno** | Right-click the request → **Generate Code**, and choose curl |

The kit's `copied_request.txt` is one, copied from a browser:

```bash
--8<-- "modules/infrastructure/everyday_tools/templates/everyday_kit/copied_request.txt"
```

Notice the `authorization` line. That's a login token. It's fine in a file on your own computer, and **never** fine in code you commit.

## Step 3: Try it in the terminal

Before writing a test, send the request once and look at the answer. A short version of the same request:

```bash
curl -s https://dummyjson.com/products/add \
  -H 'content-type: application/json' \
  --data-raw '{"title":"Practice book","price":24.5}'
```

```text
{"id":195,"title":"Practice book","price":24.5}
```

[DummyJSON](https://dummyjson.com/docs/products) is a free practice API: it answers like a real shop, but saves nothing. The answer has an `id` (made by the server) and the `title` and `price` we sent.

## Step 4: Decide what the test should check

A test that only checks "it didn't crash" catches little. Look at the answer and pick what matters:

| Check | Here | Why |
| --- | --- | --- |
| The status | Below 400 | The request worked |
| What you sent comes back | `title` is `"Practice book"` | The server saved what you asked |
| What the server makes | `id` is there and is a number | The new product has an id to find it by |
| What the spec says | Read the ticket or API docs | Maybe the price must have 2 decimals, or a new product must be hidden |

## Step 5: Turn it into a test

```bash
python curl_to_pytest.py copied_request.txt > tests/test_from_curl.py
```

```text
Moved out of the test: authorization. Set them as environment variables before running it.
```

The script keeps the address, the body and the useful headers. It drops the browser noise (`user-agent`, `accept-language`, `origin`...). It moves the token out of the code. `tests/test_from_curl.py` now has:

```python
# Made by curl_to_pytest.py from myOpenSDET. Check it, then change the checks.
import os

import requests

BASE_URL = os.environ.get("BASE_URL", 'https://dummyjson.com')


def test_post_products_add():
    headers = {'accept': 'application/json'}
    if os.environ.get("API_AUTH"):  # never paste the real value here
        headers['authorization'] = os.environ["API_AUTH"]
    answer = requests.request(
        'POST',
        f"{BASE_URL}/products/add",
        headers=headers,
        json={'title': 'Practice book', 'price': 24.5},
        timeout=10,
    )
    assert answer.status_code < 400, f"{answer.status_code}: {answer.text[:200]}"
    # CHANGE: add the checks that matter, for example:
    # assert answer.json()["id"] == 1
```

Two things make it reusable on your own app:

- **`BASE_URL`** comes from an environment variable, so the same test runs on the test site and on staging.
- **Login headers** (`Authorization`, `Cookie`, `X-Api-Key`) come from `API_AUTH`, `API_COOKIE` and `API_KEY`. The real values stay in your terminal.

On your own app, copy your request into a text file, or paste it straight in: `pbpaste | python curl_to_pytest.py > tests/test_my_request.py` on macOS.

## Step 6: Give it the token, outside the code

Set the token for this terminal only, then run the test:

=== "macOS, Linux, Git Bash"

    ```bash
    export API_AUTH="Bearer <your token>"
    export BASE_URL=https://test.your-app.example
    ```

=== "Windows PowerShell"

    ```powershell
    $env:API_AUTH = "Bearer <your token>"
    $env:BASE_URL = "https://test.your-app.example"
    ```

The DummyJSON example needs neither, so you can skip this step for now. In a pipeline, these come from the pipeline's secret settings.

## Step 7: Run it and add real checks

```bash
python -m pytest -v tests
```

```text
collecting ... collected 1 item

tests/test_from_curl.py::test_post_products_add PASSED                   [100%]

============================== 1 passed in 0.27s ===============================
```

Now replace the `CHANGE` comment with the checks from step 4. To see what a failure looks like, here the second check is wrong on purpose:

```python
    assert answer.json()["title"] == "Practice book"
    assert answer.json()["id"] == 1
```

```text
>       assert answer.json()["id"] == 1
E       assert 195 == 1

tests/test_from_curl.py:23: AssertionError
=========================== short test summary info ============================
FAILED tests/test_from_curl.py::test_post_products_add - assert 195 == 1
1 failed in 0.27s
```

pytest shows the line and both values: the server gave `195`, the test expected `1`. Here the test is wrong (the id is new each time), so check `isinstance(answer.json()["id"], int)` instead. On a real app, ask: is the test wrong, or the app?

## Step 8: Debug the test in VS Code

When a test fails and the message isn't enough, stop it in the middle and look around.

**Set up once:**

1. Rename the kit's `vscode` folder to **`.vscode`** (with the dot). VS Code reads its settings from there.
2. VS Code asks to install the recommended extensions (Python, Python Debugger, Ruff, Playwright, REST Client). Say yes, or open them from the Extensions view.
3. Choose your Python: **Ctrl+Shift+P** (Cmd+Shift+P on macOS) → **Python: Select Interpreter**.

**Debug:**

1. Open `tests/test_from_curl.py`. Click left of a line number, on the `assert` line: a **red dot** appears. That's a **breakpoint**: the test will pause there.
2. Open **Run and Debug** (Ctrl+Shift+D), choose **Debug the tests in this file**, press **F5**.
3. The test stops on the red dot. The **Variables** panel shows `answer`, `headers` and the rest. In the **Debug Console**, type `answer.json()` and press Enter to see the whole answer.
4. **F10** runs one more line. **F5** runs on to the next breakpoint, or to the end.

The second setting, **Debug the tests that failed last time**, runs only the failures from your last run. The kit's `launch.json`:

```json
--8<-- "modules/infrastructure/everyday_tools/templates/everyday_kit/vscode/launch.json"
```

The **Testing** view (the flask icon) lists every test, with a play button and a debug button next to each one. `settings.json` turns it on for pytest.

For reading the code you're debugging, see the [debugging toolkit](../debugging-toolkit/index.md). For searching big log files, see [Linux and shell](../linux-and-shell/index.md#step-4-search-with-grep).

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| `Paste a command that starts with curl` | The file or paste isn't a curl command (maybe it's PowerShell or fetch) | In the browser, pick **Copy as cURL (bash)**, not "cmd" or "PowerShell" |
| `No address found in the curl command` | The address got lost in copying | Copy again. The address starts with `http` |
| `FileNotFoundError: [Errno 2] No such file or directory: 'nothere.txt'` | Wrong file name, or wrong folder | `ls` to see the files in this folder |
| `ModuleNotFoundError: No module named 'requests'` | The packages aren't installed for this Python | `python -m pip install -r requirements.txt`, and check the interpreter VS Code uses (step 8) |
| `401` or `403` in the assert message | The token is missing or old | Set `API_AUTH` again (step 6). Tokens copied from a browser expire |
| The same test passes for you and fails in the pipeline | The pipeline has another `BASE_URL`, or no token | Check the pipeline's variables and secrets |
| The breakpoint is grey, and the test doesn't stop | VS Code uses another Python, or the line never runs | Select the interpreter (step 8). Put the breakpoint on an earlier line |

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/arshaduzzaman-sm/myopensdet/tree/main/modules/infrastructure/everyday_tools/templates).

=== "curl_to_pytest.py"

    ```python
    --8<-- "modules/infrastructure/everyday_tools/templates/everyday_kit/curl_to_pytest.py"
    ```

=== "settings.json"

    ```json
    --8<-- "modules/infrastructure/everyday_tools/templates/everyday_kit/vscode/settings.json"
    ```

=== "extensions.json"

    ```json
    --8<-- "modules/infrastructure/everyday_tools/templates/everyday_kit/vscode/extensions.json"
    ```

## References

- [Chrome DevTools: Network panel](https://developer.chrome.com/docs/devtools/network)
- [curl manual](https://curl.se/docs/manpage.html)
- [Postman: generate code snippets](https://learning.postman.com/docs/sending-requests/create-requests/generate-code-snippets/)
- [Bruno documentation](https://docs.usebruno.com/)
- [VS Code: Python testing](https://code.visualstudio.com/docs/python/testing)
- [VS Code: Python debugging](https://code.visualstudio.com/docs/python/debugging)
- [Requests: quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [DummyJSON: products](https://dummyjson.com/docs/products)

Written for Python 3.13, pytest 9.2 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
