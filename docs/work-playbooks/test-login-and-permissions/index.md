---
title: "How to Test Login, Tokens and Permissions in an API, Step by Step"
description: "A step-by-step guide to testing authentication and authorization at work: learn how your app logs in, list who may do what, plan, and copy ready pytest tests for login answers, tokens, logout and access to other users' data and admin pages. Then run them, read the results and fix the common errors."
level: Beginner
tags:
  - API
  - Security
  - Templates
nav_title: "Test login and permissions, step by step"
order: 35
group: "Login and access"
summary: "How login works, who may do what, ready tests for tokens and access, run, read."
updated: "2026-11-22"
---

# How to Test Login, Tokens and Permissions in an API, Step by Step

Login bugs are the ones that end up in the news: a customer who can read another customer's orders, a normal user who can open admin pages, a "logged out" session that still works. This guide takes you from nothing to automated login and permission tests: what to find out, what to check, and ready templates to copy. Follow the steps in order.

!!! example "The situation"
    **Your lead:** "We're adding orders to the customer app. Before release, can you make sure people can only see their own orders, and that login and logout really work?"

You'll practise on a **small practice API** that runs on your own computer. It has login, tokens, orders and an admin page, and three access bugs of the kind real apps ship. When you finish, you point the same tests at your own app.

!!! danger "Only test what you're allowed to test"
    Run these tests on your team's test environment, with test-only accounts. Never on production, never on someone else's app, never with real customers' accounts.

## Step 1: Install what you need

You need **Python 3.13** and **VS Code**. If you don't have them, follow [environment setup](../../start-here/environment-setup/index.md) first.

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/work_playbooks/test_login_and_permissions/templates). Then open the `auth_tests` folder in VS Code (**File → Open Folder**).

2. **Open a terminal** in VS Code (**Terminal → New Terminal**), make a virtual environment and install pytest and requests:

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

3. **Start the practice API** in this terminal. It needs no packages, and only your computer can reach it:

    ```bash
    python practice_api.py
    ```

    ```text
    Practice API (with planted bugs) on http://127.0.0.1:8765  (Ctrl+C to stop)
    ```

    Leave it running. Open a **second terminal** (the **+** in the terminal panel) for the next steps, and activate `.venv` there too.

!!! success "Check"
    The "Practice API" line in the first terminal, and `(.venv)` in the second. If not, see [when it goes wrong](#step-9-when-it-goes-wrong).

## Step 2: Find out how login works

**At work, find out five things.** Ask the developer, or read the API spec:

| Find out | Practice API |
| --- | --- |
| **How you log in** | `POST /api/login` with `{"email": ..., "password": ...}` |
| **What comes back** | A token in the answer. Other apps use a cookie |
| **How the token is sent** | Header `Authorization: Bearer <token>` |
| **How long a token lives**, and is there a refresh token | Until logout |
| **The roles**, and what each may do | `customer`: own orders. `admin`: also the user list |

And ask for **three test accounts**: two normal users (A and B, each with some data) and one admin. Two normal users are the key: most permission bugs are "user A can see user B's data".

**Then try it by hand.** Log in:

```bash
curl -i -X POST http://127.0.0.1:8765/api/login -H "Content-Type: application/json" -d '{"email": "arshad.test@example.com", "password": "local_only_password"}'
```

```text
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 120

{"token": "<random token, hidden here>", "user": {"email": "arshad.test@example.com", "id": 1, "role": "customer"}}
```

The token is a random string, new at every login. We hid it above: **a token is a password for a while**, so keep it out of tickets, chats and screenshots too.

Put your token in a variable and use it:

```bash
TOKEN=<paste your token here>
curl http://127.0.0.1:8765/api/me -H "Authorization: Bearer $TOKEN"
```

```text
{"email": "arshad.test@example.com", "id": 1, "role": "customer"}
```

Without a token, the API says no, as it should:

```text
HTTP/1.0 401 Unauthorized
{"error": "Log in first"}
```

## Step 3: Decide which tests you need

Two words you'll hear: **authentication** is "who are you?" (login and tokens). **Authorization** is "what may you do?" (permissions). Test both.

| Kind | Common tests |
| --- | --- |
| **Login** | Right user gets a token. Wrong password is refused. **An unknown email gets exactly the same answer as a wrong password**. Broken requests get 400, not a crash. The password never comes back in the answer |
| **Tokens** | No token: 401. Made-up token: 401. A token with one letter changed: 401. The token opens the right account. **After logout the token stops working.** After it expires, it stops working |
| **Permissions** | A user reads their own data. **A user can't read another user's data**, in both directions. A normal user can't open admin pages. An admin can |

Status codes to expect: **401** means "log in first". **403** means "you're logged in, but not allowed". For someone else's record, **404** is also fine: it doesn't even admit the record exists.

## Step 4: Write a one-page plan

Copy `test_plan.md` from the project and fill it in:

1. **How login works:** the five answers from step 2.
2. **Test users:** who they are, and what data each one owns.
3. **Who may do what:** a table with one row per page and one column per kind of user.
4. **Checks:** the kinds from step 3.
5. **Questions for the team.** 6. **Not in this plan.**

The "who may do what" table is the heart of it:

```markdown
| Page or action | Not logged in | Owner | Another user | Admin |
| --- | --- | --- | --- | --- |
| GET /api/orders/{id} | 401 | 200 | 403 or 404 | 200? |
| GET /api/admin/users | 401 | 403 | 403 | 200 |
```

Each cell is a test. The cell with a `?` is a question for the team. Post the plan in the ticket.

## Step 5: Set up the project

```text
auth_tests/
├── requirements.txt       pytest and requests
├── pytest.ini             pytest settings
├── test_plan.md           your plan (step 4)
├── practice_api.py        the practice API (not needed for your own app)
└── tests/
    ├── conftest.py        your app's paths, how it logs in, the test users
    ├── test_login.py      login answers
    ├── test_tokens.py     tokens and logout
    └── test_permissions.py  who may read what
```

`tests/conftest.py` holds everything about **your** app. Change the parts marked `CHANGE`:

```python
--8<-- "modules/work_playbooks/test_login_and_permissions/templates/auth_tests/tests/conftest.py"
```

| Part | What it is |
| --- | --- |
| `USER_A`, `USER_B`, `ADMIN` | Read from the terminal as `email:password`. Never written in a file |
| `log_in()`, `headers_for()` | How your app logs in and sends the token. Change these two if your app uses a form or a cookie |
| `HiddenHeaders` | Prints the token as `***`, so it never shows in a failure message |
| `user_a`, `user_b`, `admin` | Fixtures: headers of a logged-in user. A test that needs one is skipped if that user isn't set |

## Step 6: Copy the test templates

=== "Login"

    ```python
    --8<-- "modules/work_playbooks/test_login_and_permissions/templates/auth_tests/tests/test_login.py"
    ```

=== "Tokens"

    ```python
    --8<-- "modules/work_playbooks/test_login_and_permissions/templates/auth_tests/tests/test_tokens.py"
    ```

    The logout test logs in on its own, so it never ends the token another test is using.

=== "Permissions"

    ```python
    --8<-- "modules/work_playbooks/test_login_and_permissions/templates/auth_tests/tests/test_permissions.py"
    ```

    For each row of your "who may do what" table, copy one test and change the path.

## Step 7: Run the tests

### Set the test users

In the second terminal (never in a file):

=== "macOS / Linux"

    ```bash
    export USER_A="arshad.test@example.com:local_only_password"
    export USER_B="mia.khan@example.com:local_only_password"
    export ADMIN="admin@example.com:local_only_password"
    ```

=== "Windows"

    ```powershell
    $env:USER_A="arshad.test@example.com:local_only_password"
    $env:USER_B="mia.khan@example.com:local_only_password"
    $env:ADMIN="admin@example.com:local_only_password"
    ```

### Run

```bash
python -m pytest
```

```text
tests/test_login.py::test_right_login_gives_a_token PASSED               [  6%]
tests/test_login.py::test_wrong_password_is_refused PASSED               [ 12%]
tests/test_login.py::test_unknown_user_gets_the_same_answer_as_a_wrong_password FAILED [ 18%]
tests/test_login.py::test_bad_login_requests_get_400_not_a_crash[empty] PASSED [ 25%]
tests/test_login.py::test_bad_login_requests_get_400_not_a_crash[no password] PASSED [ 31%]
tests/test_login.py::test_bad_login_requests_get_400_not_a_crash[not json] PASSED [ 37%]
tests/test_permissions.py::test_user_can_read_their_own_record PASSED    [ 43%]
tests/test_permissions.py::test_user_cannot_read_another_users_record FAILED [ 50%]
tests/test_permissions.py::test_other_user_cannot_read_user_as_record FAILED [ 56%]
tests/test_permissions.py::test_normal_user_cannot_open_the_admin_page PASSED [ 62%]
tests/test_permissions.py::test_admin_can_open_the_admin_page PASSED     [ 68%]
tests/test_tokens.py::test_no_token_gets_401 PASSED                      [ 75%]
tests/test_tokens.py::test_made_up_token_gets_401 PASSED                 [ 81%]
tests/test_tokens.py::test_changed_token_gets_401 PASSED                 [ 87%]
tests/test_tokens.py::test_token_opens_the_right_account PASSED          [ 93%]
tests/test_tokens.py::test_token_stops_working_after_logout FAILED       [100%]
...
========================= 4 failed, 12 passed in 0.07s =========================
```

## Step 8: Read the results

**12 passed:** login works, bad requests don't crash it, made-up and changed tokens are refused, and normal users can't open the admin page.

**4 failed.** Read the first line of each:

```text
E       AssertionError: unknown user: {'error': 'No such user'}, wrong password: {'error': 'Wrong email or password'}
E       AssertionError: user A read user B's record: {"id": 102, "user_id": 2, "total": "15.99"}
E       AssertionError: user B read user A's record: {"id": 101, "user_id": 1, "total": "64.48"}
E       AssertionError: the token still works after logout
```

| Failure | What it means | How bad |
| --- | --- | --- |
| User A read user B's order, and B read A's | **Any logged-in user can read any order** by changing the number in the address. Testers call this **IDOR** (insecure direct object reference). One bug, two failing tests | **Critical.** Report first. Every customer's orders are open to every other customer |
| Token still works after logout | Logout only "forgets" the token in the app. Someone who copied it can keep using it | **High** |
| "No such user" vs "Wrong email or password" | The login tells strangers which emails have an account. Attackers use that to pick targets | **Medium.** Ask the team: some apps accept this on purpose |

To see what "fixed" looks like, stop the practice API (**Ctrl+C**), start it with the bugs fixed, and run again:

```bash
python practice_api.py --fixed
```

```text
============================== 16 passed in 0.04s ==============================
```

Two things to notice:

- **The token never shows in the output.** The failure reads `get('/api/me', {'Authorization': '***'})`: that's `HiddenHeaders` working. Test reports get shared, so tokens in them would be a leak too.
- **Write the bug report with the request, not the token.** Say "logged in as user A, `GET /api/orders/102` returned user B's order". Leave out tokens and passwords.

### Use it on your own app

1. In `conftest.py`: set `BASE_URL` and the paths. Pick one record owned by user A and one owned by user B.
2. If your app logs in with a form or a cookie, change `log_in()` and `headers_for()`. Check the answer by hand with curl first, as in step 2.
3. Set `USER_A`, `USER_B` and `ADMIN` to test-only accounts.
4. Run `test_login.py` first. Once it passes, run the rest.
5. Add one permission test for each row of your "who may do what" table.

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| `SKIPPED ... Set USER_A="email:password" to run this test` | The user isn't set in **this** terminal, or it has no `:` between email and password | Step 7, set the test users. A new terminal forgets them |
| `AssertionError: USER_A could not log in: 401` | Wrong email or password in `USER_A`, or the login path or body is different in your app | Log in by hand with curl (step 2), then fix `USER_A` or `log_in()` |
| `ConnectionError: ... port=8765 ... [Errno 61] Connection refused` | Nothing is running at `BASE_URL` | Start `python practice_api.py` in the first terminal. For your app, check `BASE_URL` |
| `OSError: [Errno 48] Address already in use` (when starting the practice API) | It's already running in another terminal | Use the one that's running, or stop it with **Ctrl+C** |
| Every permission test passes, even on an app you know is wrong | `A_RECORD_PATH` and `B_RECORD_PATH` point to the same owner, or to records that don't exist | Check by hand: user A gets 200 on `A_RECORD_PATH` |
| `401` on every test that needs a login | The token is sent the wrong way: wrong header name, missing `Bearer`, or the app wants a cookie | Change `headers_for()` to match what works in curl |
| The account gets locked during the tests | The app locks accounts after a few wrong passwords | Ask for a test account without lockout, or run the wrong-password tests less often |

When you're done: **Ctrl+C** in the first terminal stops the practice API.

Still stuck? Go deeper:

- [Authentication in API tests](../../core-automation/api-testing/authentication.md): tokens, API keys, cookies
- [Status codes](../../core-automation/api-testing/status-codes.md): 401, 403, 404 and the rest
- [Security testing](../../advanced-testing/security-testing/index.md): the bigger picture
- [Automate API tests, step by step](../automate-api-tests/index.md): the GET, POST, PUT and DELETE tests that go with these

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/myopensdet/myopensdet.github.io/tree/main/modules/work_playbooks/test_login_and_permissions/templates).

=== "test_plan.md"

    ```markdown
    --8<-- "modules/work_playbooks/test_login_and_permissions/templates/auth_tests/test_plan.md"
    ```

=== "practice_api.py"

    ```python
    --8<-- "modules/work_playbooks/test_login_and_permissions/templates/auth_tests/practice_api.py"
    ```

## References

- [OWASP: Authentication cheat sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP: Authorization testing (Web Security Testing Guide)](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/README)
- [OWASP: Insecure direct object references](https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html)
- [MDN: 401 Unauthorized](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/401) and [403 Forbidden](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/403)
- [Requests: Quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)

Written for Python 3.13, pytest 9 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
