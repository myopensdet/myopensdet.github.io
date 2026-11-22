---
title: "How to Automate UI Tests With Playwright and pytest, Step by Step"
description: "A step-by-step guide to UI test automation at work: install Playwright for Python, read the feature, pick the user flows, plan, and copy ready pytest tests for login, product lists, cart and checkout. Then run them in any browser, read failures with screenshots and traces, and fix the common errors."
level: Beginner
tags:
  - UI
  - Playwright
  - Templates
nav_title: "Automate UI tests, step by step"
order: 40
group: "UI work"
summary: "Install, pick the flows, plan, copy ready tests, run, read screenshots and traces."
updated: "2026-11-22"
---

# How to Automate UI Tests With Playwright and pytest, Step by Step

You've been asked to automate tests for a web app's pages, and you don't know where to start. This guide takes you from nothing to working UI tests: what to install, what to look at, which tests to write, and ready templates to copy. Follow the steps in order.

!!! example "The situation"
    **Your lead:** "We test the shop by hand before every release, and it takes half a day. Can you automate the main flows: log in, the product list, the cart and checkout?"

You'll practise on **Sauce Demo** (`https://www.saucedemo.com`), a free practice shop that Sauce Labs runs for exactly this. Its demo users and password are printed on its own login page. Some of those users have bugs built in, so your tests will find real bugs. When you finish, you point the same tests at your own app.

## Step 1: Install what you need

You need **Python 3.13** and **VS Code**. If you don't have them, follow [environment setup](../../start-here/environment-setup/index.md) first.

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/arshaduzzaman-sm/myopensdet/tree/main/modules/work_playbooks/automate_ui_tests/templates). Then open the `ui_tests` folder in VS Code (**File → Open Folder**).

2. **Open a terminal** in VS Code (**Terminal → New Terminal**), make a virtual environment and install the packages. **pytest** runs the tests; **Playwright** drives the browser; **pytest-playwright** joins the two.

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

    The last line should be:

    ```text
    Successfully installed greenlet-3.5.6 iniconfig-2.3.1 packaging-26.3 playwright-1.64.1 pluggy-1.7.0 pyee-14.0.0 pygments-2.21.0 pytest-9.2.0 pytest-playwright-0.10.0 python-slugify-9.1.3 text-unidecode-1.3 typing-extensions-4.16.0
    ```

3. **Download the browser** (once per computer, it takes a minute or two):

    ```bash
    python -m playwright install chromium
    ```

!!! success "Check"
    `(.venv)` at the start of your prompt, and no red error. If not, see [when it goes wrong](#step-9-when-it-goes-wrong).

## Step 2: Read the feature, and try it by hand

**At work, get four things first:**

| Ask for | Why |
| --- | --- |
| **The ticket or user story**, with its acceptance criteria | What the page must do, in the team's words |
| **The test site address** | Never automate against production unless your team says so in writing |
| **Test users**, one per role | Test-only accounts. Never your own, never a real customer's |
| **"Do elements have test ids?"** | Attributes like `data-testid="checkout"` make tests stable. If there are none, ask the developers to add them |

**Then use the feature yourself**, slowly, and write down:

- **The flows**: the steps a person takes, in order. For the shop: log in → add a product → open the cart → check out → fill the form → finish.
- **What you see at each step**: a title, a count, a total, a message.
- **The rules**: which fields are required, what the error messages say, what happens on a wrong password.

To find how Playwright should point at each button and box, let it watch you:

```bash
python -m playwright codegen https://www.saucedemo.com
```

A browser opens with a second window. Click around; the second window writes the Python lines for every click, like `page.get_by_placeholder("Username").fill(...)`. Copy the **locators** (the part that finds the element), not the whole script.

## Step 3: Decide which tests you need

UI tests are slow, so keep them for what only a page can show: **flows a person takes, and what they see.** Leave detailed rules (every bad value, every limit) to [API tests](../automate-api-tests/index.md), which run much faster.

Almost every web app needs these kinds of UI tests:

| Kind | Common tests |
| --- | --- |
| **Login** | Right user gets in. Wrong password shows an error. Empty fields show an error |
| **Access** | Pages need a login. Logout really logs out |
| **Lists** | Every item has a name, a price and its own picture. Sorting and filtering really sort and filter |
| **Numbers on screen** | Counts and badges update. Totals add up |
| **Forms** | Each required field shows its own error. What you type stays in the box |
| **Main flow** | The whole flow, start to end, lands on the right page |
| **State** | The cart is still there after a reload |

## Step 4: Write a one-page plan

Copy `test_plan.md` from the project and fill it in:

1. **What and where:** the ticket, the test site, the test users, test ids, which browsers.
2. **User flows:** the steps and what a person should see at the end.
3. **Checks:** the kinds from step 3, with a box to tick when automated.
4. **Questions for the team.**
5. **Not in this plan:** what API tests, visual tests or speed tests cover instead.

Part of the plan for the shop:

```markdown
| Flow | Steps a person takes | What they should see at the end |
| --- | --- | --- |
| Log in | Open the site, type user and password, press Login | The products page |
| Buy one product | Add to cart, open cart, checkout, fill the form, finish | "Thank you for your order!", empty cart |
```

Post it in the ticket. Your lead may say "skip sorting, add the discount code". Better to hear that now.

## Step 5: Set up the project

```text
ui_tests/
├── requirements.txt       pytest, Playwright, pytest-playwright
├── pytest.ini             screenshots and traces when a test fails
├── test_plan.md           your plan (step 4)
└── tests/
    ├── conftest.py        the site, the login, shared helpers
    ├── test_login.py      login and access
    ├── test_products.py   the product list and sorting
    ├── test_cart.py       the cart
    └── test_checkout.py   the form, the totals, the order
```

`tests/conftest.py` holds everything about **your** app. Change the four parts marked `CHANGE`:

```python
--8<-- "modules/work_playbooks/automate_ui_tests/templates/ui_tests/tests/conftest.py"
```

| Part | What it is |
| --- | --- |
| `page` | Comes from pytest-playwright. Every test gets a **fresh browser profile**: no login, no cart, nothing from the test before |
| `base_url` | So tests say `page.goto("/inventory.html")`, not the full address |
| `logged_in` | A page that is already logged in. Skips the test if no user is set |
| `set_test_id_attribute` | Lets `get_by_test_id("error")` find `data-test="error"` |

`pytest.ini` keeps evidence of every failure:

```ini
--8<-- "modules/work_playbooks/automate_ui_tests/templates/ui_tests/pytest.ini"
```

**How to point at elements**, best first:

1. `get_by_role("button", name="Login")`: what a person sees. Survives most redesigns.
2. `get_by_placeholder("Username")` or `get_by_label("Email")`: for boxes.
3. `get_by_test_id("checkout")`: when the developers added test ids.
4. CSS like `.btn_primary`: last choice. It breaks when someone renames a style.

**How to check**: always with `expect(...)`. It waits until the page matches (5 seconds here), so tests don't fail just because a page was slow. Never use `time.sleep()`.

## Step 6: Copy the test templates

Each file follows step 3. Each test is short: do what a person does, then `expect` what they should see.

=== "Login"

    ```python
    --8<-- "modules/work_playbooks/automate_ui_tests/templates/ui_tests/tests/test_login.py"
    ```

=== "Products"

    ```python
    --8<-- "modules/work_playbooks/automate_ui_tests/templates/ui_tests/tests/test_products.py"
    ```

    Reading a list with `all_inner_texts()` doesn't wait. Wait for the first item with `expect` first, as the first test does.

=== "Cart"

    ```python
    --8<-- "modules/work_playbooks/automate_ui_tests/templates/ui_tests/tests/test_cart.py"
    ```

=== "Checkout"

    ```python
    --8<-- "modules/work_playbooks/automate_ui_tests/templates/ui_tests/tests/test_checkout.py"
    ```

    `parametrize` runs one test three times, once for each required field. Add a row for each new field.

## Step 7: Run the tests

### Set the test user

Set the user in the terminal (never in a file). For the practice shop, use the user and password printed on its login page:

=== "macOS / Linux"

    ```bash
    export APP_USERNAME=standard_user
    export APP_PASSWORD=<the password shown on the login page>
    ```

=== "Windows"

    ```powershell
    $env:APP_USERNAME="standard_user"
    $env:APP_PASSWORD="<the password shown on the login page>"
    ```

### Run

```bash
python -m pytest
```

```text
tests/test_cart.py::test_adding_a_product_updates_the_cart_count[chromium] PASSED [  5%]
tests/test_cart.py::test_cart_shows_the_product_and_its_price[chromium] PASSED [ 11%]
tests/test_cart.py::test_removing_the_product_empties_the_cart[chromium] PASSED [ 16%]
tests/test_cart.py::test_cart_is_kept_after_a_reload[chromium] PASSED    [ 22%]
tests/test_checkout.py::test_each_required_field_shows_an_error[chromium-First Name-First Name is required] PASSED [ 27%]
tests/test_checkout.py::test_each_required_field_shows_an_error[chromium-Last Name-Last Name is required] PASSED [ 33%]
tests/test_checkout.py::test_each_required_field_shows_an_error[chromium-Zip/Postal Code-Postal Code is required] PASSED [ 38%]
tests/test_checkout.py::test_form_keeps_what_was_typed[chromium] PASSED  [ 44%]
tests/test_checkout.py::test_totals_add_up[chromium] PASSED              [ 50%]
tests/test_checkout.py::test_order_is_placed_and_the_cart_is_emptied[chromium] PASSED [ 55%]
tests/test_login.py::test_valid_login_opens_the_products_page[chromium] PASSED [ 61%]
tests/test_login.py::test_wrong_password_shows_an_error[chromium] PASSED [ 66%]
tests/test_login.py::test_empty_username_shows_an_error[chromium] PASSED [ 72%]
tests/test_login.py::test_pages_need_a_login[chromium] PASSED            [ 77%]
tests/test_login.py::test_logout_returns_to_the_login_page[chromium] PASSED [ 83%]
tests/test_products.py::test_every_product_has_a_name_a_price_and_its_own_picture[chromium] PASSED [ 88%]
tests/test_products.py::test_sort_by_price_low_to_high[chromium] PASSED  [ 94%]
tests/test_products.py::test_sort_by_name_z_to_a[chromium] PASSED        [100%]

============================= 18 passed in 12.89s ==============================
```

### Useful ways to run


| Command | What it does |
| --- | --- |
| `python -m pytest --headed --slowmo 500` | Shows the browser, half a second per action, so you can watch |
| `python -m pytest --browser firefox` | Runs in Firefox (first `python -m playwright install firefox`). Also `webkit`, Safari's engine |
| `python -m pytest -k checkout` | Runs only tests with "checkout" in the name |
| `python -m pytest --lf` | Runs only the tests that failed last time |

## Step 8: Read the results

All 18 passed for `standard_user`. Now run the same tests as `problem_user`, a demo user with bugs built in, the way a bad release would have them:

```bash
export APP_USERNAME=problem_user
python -m pytest
```

```text
FAILED tests/test_checkout.py::test_each_required_field_shows_an_error[chromium-First Name-First Name is required]
FAILED tests/test_checkout.py::test_each_required_field_shows_an_error[chromium-Zip/Postal Code-Postal Code is required]
FAILED tests/test_checkout.py::test_form_keeps_what_was_typed[chromium] - Ass...
FAILED tests/test_checkout.py::test_totals_add_up[chromium] - AssertionError:...
FAILED tests/test_checkout.py::test_order_is_placed_and_the_cart_is_emptied[chromium]
FAILED tests/test_products.py::test_every_product_has_a_name_a_price_and_its_own_picture[chromium]
FAILED tests/test_products.py::test_sort_by_price_low_to_high[chromium] - Ass...
FAILED tests/test_products.py::test_sort_by_name_z_to_a[chromium] - Assertion...
=================== 8 failed, 10 passed in 60.21s (0:01:00) ====================
```

Eight failures don't mean eight bugs. **Read the first lines of each failure, and group them:**

```text
E           AssertionError: Locator expected to have Value 'Arshad'
E           Actual value: Test
E           Call log:
E             - Expect "to_have_value" get_by_placeholder("First Name") with timeout 5000ms
E             - waiting for get_by_placeholder("First Name")
```

The First Name box holds `Test`, the last name.

```text
E       AssertionError: products share pictures: ['/assets/sl-404-Cq1a9k9X.jpg', '/assets/sl-404-Cq1a9k9X.jpg', '/assets/sl-404-Cq1a9k9X.jpg', '/assets/sl-404-Cq1a9k9X.jpg', '/assets/sl-404-Cq1a9k9X.jpg', '/assets/sl-404-Cq1a9k9X.jpg']
E       AssertionError: not sorted: [29.99, 9.99, 15.99, 49.99, 7.99, 15.99]
```

| Failures | The one bug behind them | Group |
| --- | --- | --- |
| Form keeps what was typed; the two field errors; totals; order placed | **Typing the last name writes it into the First Name box.** Last Name stays empty, so every checkout fails with "Last Name is required" | **Bug**, the worst one: nobody can buy |
| Every product has its own picture | All six products show the same broken picture | **Bug** |
| Sort by price, sort by name | Choosing a sort order does nothing | **Bug** |

So: **three bugs, one blocking.** Report the blocking one first. A wall of red after a release is often one bug that breaks many tests.

**See exactly what happened.** For every failed test, `test-results/` has a screenshot (`test-failed-1.png`) and a **trace**: a recording of every step with the page before and after each click. Open it:

```bash
python -m playwright show-trace test-results/tests-test-products-py-test-sort-by-name-z-to-a-chromium/trace.zip
```

Click any step on the left to see the page at that moment. Attach the screenshot to the bug report.

!!! warning "Traces record what was typed, passwords too"
    We checked: the password never shows in pytest's output, but it **is** inside `trace.zip`, because the trace records every `fill()`. Use test-only accounts, and never attach traces from real accounts to tickets or public places. `test-results/` is in `.gitignore`, so it never goes into Git.

### Use it on your own app

1. In `conftest.py`: set `BASE_URL`, your test id attribute, and the steps of your login page.
2. Set `APP_USERNAME` and `APP_PASSWORD` to a test-only user.
3. Run `python -m playwright codegen <your site>` and copy the locators for your pages.
4. Change the test files one at a time: first `test_login.py`, run it until it passes, then the next.
5. Delete what your app doesn't have. Add tests for your own flows the same way: do what a person does, `expect` what they should see.

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| `SKIPPED ... Set APP_USERNAME and APP_PASSWORD to run tests that need a login` | The user isn't set in **this** terminal | Step 7, set the test user. A new terminal forgets it |
| `Executable doesn't exist at ...` and `Please run the following command to download new browsers: playwright install` | The browser isn't downloaded, or Playwright was updated | `python -m playwright install chromium` |
| `error: unrecognized arguments: --screenshot --tracing --output` | pytest-playwright isn't installed, or the virtual environment isn't active | Activate `.venv`, then `python -m pip install -r requirements.txt` |
| `Page.goto: net::ERR_NAME_NOT_RESOLVED at https://www.saucedemoo.com/...` | A typo in the site address, or no internet or VPN | Check `BASE_URL` |
| `TimeoutError: Locator.click: Timeout 30000ms exceeded.` and `waiting for get_by_role("link", name="Logout")` | Nothing on the page matches the locator. Here the "link" wasn't a real link | Open `--headed`, or run `codegen` and copy the locator it writes |
| `strict mode violation: ... resolved to 3 elements` | The locator matches more than one element, so Playwright won't guess which to click | Make it narrower: add `name="..."`, or start from the row: `.filter(has_text="Backpack")` |
| `Locator expected to have text ...` / `Actual value: ...` | The page showed something else. That's the test working: a bug, or the page changed on purpose | Look at the screenshot. Ask before changing the test |
| A test passes alone but fails with the others | Tests depend on each other, or on data another test changed | Every test sets up its own data. Don't rely on order |

Still stuck? Go deeper:

- [UI automation topic](../../core-automation/ui-automation/index.md): Page Objects, waits, frames, tabs, cross-browser runs
- [Choosing locators](../../core-automation/ui-automation/choosing-locators.md) and [waits](../../core-automation/ui-automation/waits.md)
- [Screenshots and traces](../../core-automation/ui-automation/screenshots-and-traces.md)
- [Fix a flaky test](../../advanced-testing/flaky-tests-and-speed/index.md)

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/arshaduzzaman-sm/myopensdet/tree/main/modules/work_playbooks/automate_ui_tests/templates).

=== "test_plan.md"

    ```markdown
    --8<-- "modules/work_playbooks/automate_ui_tests/templates/ui_tests/test_plan.md"
    ```

=== "requirements.txt"

    ```text
    --8<-- "modules/work_playbooks/automate_ui_tests/templates/ui_tests/requirements.txt"
    ```

## References

- [Playwright for Python: Writing tests](https://playwright.dev/python/docs/writing-tests)
- [Playwright for Python: Locators](https://playwright.dev/python/docs/locators)
- [Playwright for Python: Assertions](https://playwright.dev/python/docs/test-assertions)
- [Playwright for Python: pytest plugin](https://playwright.dev/python/docs/test-runners)
- [Playwright for Python: Trace viewer](https://playwright.dev/python/docs/trace-viewer)

Written for Python 3.13, pytest 9, Playwright 1.64 and pytest-playwright 0.10. Outputs captured November 2026 on Sauce Demo. Links checked: November 2026.
