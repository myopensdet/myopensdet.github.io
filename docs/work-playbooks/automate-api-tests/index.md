---
title: "How to Automate API Tests With Python and pytest, Step by Step"
description: "A step-by-step guide to automating API tests at work: install pytest, read the developer's API spec, decide which tests you need, write a one-page plan, and copy ready test templates for GET, POST, PUT and DELETE. Then run them, read the results, and fix the common errors."
level: Beginner
tags:
  - API
  - pytest
  - Templates
nav_title: "Automate API tests, step by step"
order: 5
group: "API work"
summary: "Install, read the spec, plan, copy the GET/POST/PUT/DELETE templates, run."
updated: "2026-11-22"
---

# How to Automate API Tests With Python and pytest, Step by Step

Your team has an API, and you've been asked to automate its tests. This guide takes you from an empty folder to tests running against that API. Follow the steps in order. Each step says what to do, and what you should see when it worked.

!!! example "The situation"
    **Your lead:** "The booking API is on the test server. Here's the Swagger link. Can you write automated tests for it?"

You'll practise on **Restful-booker**, a free public API made for practice. It works like a real one: you log in, and you create, read, change and delete bookings. When you finish, you change three settings and run the same tests against your own API.

## Step 1: Install what you need

You need **Python 3.13** and **VS Code**. If you don't have them, follow [environment setup](../../start-here/environment-setup/index.md) first, then come back.

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/work_playbooks/automate_api_tests/templates). Then open the `api_tests` folder in VS Code (**File → Open Folder**).

2. **Open a terminal** in VS Code (**Terminal → New Terminal**). It opens in the `api_tests` folder.

3. **Make a virtual environment**, a private place for this project's packages:

    === "macOS / Linux"

        ```bash
        python3.13 -m venv .venv
        source .venv/bin/activate
        ```

    === "Windows"

        ```powershell
        py -3.13 -m venv .venv
        .venv\Scripts\Activate.ps1
        ```

    Your prompt now starts with `(.venv)`. Check the version:

    ```bash
    python --version
    ```

    ```text
    Python 3.13.18
    ```

4. **Install pytest and requests.** pytest runs the tests. requests sends the API calls.

    ```bash
    python -m pip install -r requirements.txt
    ```

    The last line should be:

    ```text
    Successfully installed certifi-2026.10.23 charset_normalizer-3.5.2 idna-3.20 iniconfig-2.3.1 packaging-26.3 pluggy-1.7.0 pygments-2.21.0 pytest-9.2.0 requests-2.34.2 urllib3-2.8.0
    ```

    Check pytest:

    ```bash
    python -m pytest --version
    ```

    ```text
    pytest 9.2.0
    ```

!!! success "Check"
    `(.venv)` at the start of your prompt, and `pytest 9.2.0`. If not, see [when it goes wrong](#step-9-when-it-goes-wrong).

## Step 2: Read the developer's API spec

Before writing any test, find out what the API **should** do. Ask the developer for the spec. It's usually one of these:

- A **Swagger** page (often at `/docs` or `/swagger` on the API's address)
- A **Postman collection**
- A page of API docs, like [Restful-booker's](https://restful-booker.herokuapp.com/apidoc/index.html)

For **each endpoint**, write down six things. This is what you're looking for in the spec:

| Find | Restful-booker example: `POST /booking` |
| --- | --- |
| **Method and path** | `POST /booking` |
| **What it does** | Creates a booking |
| **Login needed?** | No (but `PUT` and `DELETE` need one) |
| **What you send** (the body) | `firstname`, `lastname`, `totalprice`, `depositpaid`, `bookingdates` (`checkin`, `checkout`), `additionalneeds` |
| **What comes back** | `200`, with `bookingid` and the booking |
| **Errors** | Not written in the docs → **a question for the developer** |

The last row matters. When the spec doesn't say what happens with bad input, don't guess: write it down as a question. You'll ask it in step 4.

Then find out **how to log in**. Restful-booker: send `POST /auth` with a username and password, get a `token` back, and send it as a cookie (`Cookie: token=...`) on `PUT` and `DELETE`. Most office APIs use a header instead: `Authorization: Bearer <token>`.

## Step 3: Decide which tests you need

Almost every API has the same four kinds of endpoint. Each kind has the same common tests. Use this list for every endpoint you test:

| Method | What it does | Common tests |
| --- | --- | --- |
| **GET** | Read | It exists → `200` and the right data · It doesn't exist → `404` · A wrong id (like `abc`) → `400` or `404` · A list contains what you created |
| **POST** | Create | Valid body → created, same data comes back · A required field missing → `400` · A wrong type (text for a number) → `400` · A value that breaks a rule (checkout before checkin) → `400` |
| **PUT** | Change | It changes, and the change is **saved** (read it back) · No login → `401` or `403` · Id doesn't exist → `404` · Incomplete body → `400` |
| **DELETE** | Remove | It's gone afterwards (GET → `404`) · No login → refused, and it's **still there** · Delete twice → `404` |

Two rules make these tests trustworthy:

- **Read it back.** After `POST`, `PUT` or `DELETE`, call `GET` to check the change really happened. An API can say "done" and save nothing.
- **Never `500`.** A `500` means the server crashed. Bad input should get a polite `400`, never a crash.

## Step 4: Write a one-page plan

Copy `test_plan.md` from the project. Fill in four parts:

1. **The basics:** the API address, where the spec is, how to log in, who to ask.
2. **Endpoints and tests:** one row per endpoint, with the tests from step 3.
3. **Questions for the developer:** everything the spec doesn't say.
4. **Not in this plan:** so nobody thinks you covered it.

Here's part of the plan for Restful-booker:

```markdown
| Endpoint | What it does | Login? | Tests | Done |
| --- | --- | --- | --- | --- |
| `POST /booking` | Create a booking | No | valid: 200 and the same data back; missing field: 400; wrong type: 400; checkout before checkin: 400 | [ ] |
| `DELETE /booking/{id}` | Delete a booking | Yes | gone afterwards (GET gives 404); no login: 403 and still there; twice: 404 | [ ] |

## 3. Questions for the developer

1. What should a missing required field answer? (The docs don't say.)
2. Is a checkout date before the checkin date allowed?
3. What should PUT and DELETE answer for an id that doesn't exist?
```

**Post the plan in the ticket**, and ask the developer to read it. Ten minutes of their time now saves you writing wrong tests.

## Step 5: Set up the project

The template project has one file per method, and one shared file:

```text
api_tests/
├── requirements.txt      the packages: pytest and requests
├── pytest.ini            pytest settings
├── test_plan.md          your plan (step 4)
└── tests/
    ├── conftest.py       shared: the API address, the login, test data
    ├── test_get.py
    ├── test_post.py
    ├── test_put.py
    └── test_delete.py
```

`tests/conftest.py` is the only file you change to point at a different API. It has three parts marked `CHANGE`:

```python
--8<-- "modules/work_playbooks/automate_api_tests/templates/api_tests/tests/conftest.py"
```

What each part does:

| Part | What it is |
| --- | --- |
| `BASE_URL` | The API's address. You can also set it in the terminal, without changing the file |
| `log_in()` | How to get a token. Change the path and the body to match your API's login |
| `booking_body()` | One valid body. Tests change one field at a time: `booking_body(totalprice="abc")` |
| `api` | One connection for all tests |
| `auth_headers` | Logs in once, and gives tests the token header. If the password isn't set, login tests are skipped with a message |
| `new_booking` | Creates a booking before a test, and **deletes it afterwards**, even if the test fails |
| `HiddenHeaders` | Shows the token as `***` when a test fails, so it never lands in a log or report |

## Step 6: Copy the test templates

Each file has the common tests from step 3. Every test has the same three parts: **prepare**, **call the API**, **check the answer**.

=== "GET"

    ```python
    --8<-- "modules/work_playbooks/automate_api_tests/templates/api_tests/tests/test_get.py"
    ```

=== "POST"

    ```python
    --8<-- "modules/work_playbooks/automate_api_tests/templates/api_tests/tests/test_post.py"
    ```

    `@pytest.mark.parametrize` runs one test once per bad body. To test another bad body, add one line to the list.

=== "PUT"

    ```python
    --8<-- "modules/work_playbooks/automate_api_tests/templates/api_tests/tests/test_put.py"
    ```

=== "DELETE"

    ```python
    --8<-- "modules/work_playbooks/automate_api_tests/templates/api_tests/tests/test_delete.py"
    ```

Notice the **messages** in the checks: `f"got {response.status_code}: {response.text[:200]}"`. When a test fails, it tells you what the API actually said. Without it, you only see `assert 500 == 400`.

## Step 7: Run the tests

1. **Set the login** in the terminal. Never write passwords in a file. Restful-booker's practice login is public:

    === "macOS / Linux"

        ```bash
        export API_USERNAME=admin
        export API_PASSWORD=password123
        ```

    === "Windows"

        ```powershell
        $env:API_USERNAME="admin"
        $env:API_PASSWORD="password123"
        ```

2. **Run:**

    ```bash
    python -m pytest
    ```

    ```text
    collecting ... collected 15 items

    tests/test_delete.py::test_delete_removes_the_booking PASSED             [  6%]
    tests/test_delete.py::test_delete_without_login_is_refused PASSED        [ 13%]
    tests/test_delete.py::test_delete_twice_returns_404 FAILED               [ 20%]
    tests/test_get.py::test_get_existing_booking_returns_200_and_the_data PASSED [ 26%]
    tests/test_get.py::test_get_missing_booking_returns_404 PASSED           [ 33%]
    tests/test_get.py::test_get_with_text_id_returns_404_or_400 PASSED       [ 40%]
    tests/test_get.py::test_get_list_returns_ids PASSED                      [ 46%]
    tests/test_post.py::test_post_valid_booking_is_created PASSED            [ 53%]
    tests/test_post.py::test_post_bad_booking_is_refused_with_400[missing firstname] FAILED [ 60%]
    tests/test_post.py::test_post_bad_booking_is_refused_with_400[price is text] FAILED [ 66%]
    tests/test_post.py::test_post_bad_booking_is_refused_with_400[checkout before checkin] FAILED [ 73%]
    tests/test_put.py::test_put_updates_the_booking PASSED                   [ 80%]
    tests/test_put.py::test_put_without_login_is_refused PASSED              [ 86%]
    tests/test_put.py::test_put_missing_booking_returns_404 FAILED           [ 93%]
    tests/test_put.py::test_put_incomplete_body_returns_400 PASSED           [100%]
    ...
    ========================= 5 failed, 10 passed in 6.92s =========================
    ```

    Run one file with `python -m pytest tests/test_get.py`, or one test with `python -m pytest -k delete_twice`.

## Step 8: Read the results

**10 passed:** reading, creating, changing and deleting work, and the login is enforced.

**5 failed.** That's not your mistake: these are real problems in Restful-booker. For each failure, pytest prints what the API said. Read the `E` lines:

```text
_________ test_post_bad_booking_is_refused_with_400[missing firstname] _________
E       AssertionError: got 500: Internal Server Error
E       assert 500 == 400
```

```text
___________ test_post_bad_booking_is_refused_with_400[price is text] ___________
E       AssertionError: got 200: {"bookingid":1018,"booking":{"firstname":"Arshad","lastname":"Test","totalprice":null,...
```

```text
_____________________ test_put_missing_booking_returns_404 _____________________
E       AssertionError: got 405: Method Not Allowed
```

Sort every failure into one of two groups:

| Failure | Group | Why |
| --- | --- | --- |
| Missing `firstname` → `500` | **Bug** | The server crashed on bad input |
| `totalprice: "abc"` → saved as `null` | **Bug** | Bad data was saved |
| Checkout before checkin → saved | **Ask** | Maybe allowed? Question 2 in the plan |
| PUT to a missing id → `405` | **Ask** | Docs don't say. `404` is the usual answer. Question 3 |
| DELETE twice → `405` | **Ask** | Same as above |

Report the **bugs** (see [how to write a bug report](../../think-like-a-tester/bug-reports/index.md)). Send the **asks** to the developer. When they answer, either the API gets fixed, or you change the test to match the agreed rule. Either way, the test now protects that rule.

Also notice what **didn't** happen: the failing tests that wrongly created bookings deleted them again, and the token shows as `{'Cookie': '***'}` in every failure. Your test runs leave nothing behind and leak nothing.

### Use it on your own API

1. In `tests/conftest.py`: change `BASE_URL`, `log_in()` and `booking_body()`.
2. In each test file: change the path (`/booking`) and the field names (`firstname`, `totalprice`).
3. Set `API_USERNAME` and `API_PASSWORD` for your test account, and run `python -m pytest`.

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| `command not found: python3.13` (Windows: `py -3.13` fails) | Python 3.13 isn't installed | [Environment setup](../../start-here/environment-setup/index.md) |
| `No module named pytest` | The virtual environment isn't active, or packages aren't installed | `source .venv/bin/activate` (Windows: `.venv\Scripts\Activate.ps1`), then `python -m pip install -r requirements.txt` |
| `SKIPPED ... Set API_USERNAME and API_PASSWORD to run tests that need a login` | The login isn't set in **this** terminal | Step 7.1. A new terminal forgets it |
| `Login answered without a token: {"reason":"Bad credentials"}` (or `Login failed: 401 ...`) | Wrong username or password, or your API logs in differently | Check the account; change `log_in()` to match the spec |
| `ConnectionError` / `Max retries exceeded` | Wrong `BASE_URL`, VPN off, or the server is down | Open the address in a browser first |
| Every test that needs a login gets `401` or `403` | The token goes in the wrong place | Check the spec: cookie, or `Authorization: Bearer ...` |
| `requests.exceptions.ReadTimeout: ... Read timed out.` | The API took longer than 15 seconds | Is the test server slow or asleep? Try again, or raise `timeout` |

Still stuck? Go deeper on each part:

- [How HTTP works](../../core-automation/api-testing/how-http-works.md) and [status codes](../../core-automation/api-testing/status-codes.md)
- [HTTP methods](../../core-automation/api-testing/http-methods.md) and [authentication](../../core-automation/api-testing/authentication.md)
- [Fixtures and conftest](../../core-automation/pytest-framework/fixtures-and-conftest.md) and [parametrize](../../core-automation/pytest-framework/parametrize.md)
- [The full API testing topic](../../core-automation/api-testing/index.md)

## Next steps

When these tests run on your API:

- [Test a new endpoint when the docs are thin](../new-api-endpoint/index.md): probe one endpoint with many cases at once.
- [Test a whole API from its Swagger file](../api-from-openapi/index.md): list every endpoint, review the spec, check them all against it.
- [Reporting and logging](../../core-automation/reporting-and-logging/index.md): an HTML report and logs for every run.

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/work_playbooks/automate_api_tests/templates).

=== "test_plan.md"

    ```markdown
    --8<-- "modules/work_playbooks/automate_api_tests/templates/api_tests/test_plan.md"
    ```

=== "requirements.txt"

    ```text
    --8<-- "modules/work_playbooks/automate_api_tests/templates/api_tests/requirements.txt"
    ```

=== "pytest.ini"

    ```ini
    --8<-- "modules/work_playbooks/automate_api_tests/templates/api_tests/pytest.ini"
    ```

## References

- [Restful-booker API docs](https://restful-booker.herokuapp.com/apidoc/index.html)
- [pytest: Get started](https://docs.pytest.org/en/stable/getting-started.html)
- [requests: Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [MDN: HTTP response status codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status)

Written for Python 3.13, pytest 9 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
