---
title: "Page Object Model With Playwright and pytest"
description: "Build a Page Object Model framework: one class per page with its locators and actions, shared components like the header, methods that return the next page, no asserts in page objects, and fixtures that log in and fill the cart through the API."
level: Intermediate
tags:
  - Playwright
  - UI
  - Templates
nav_title: "Page Object Model"
order: 40
summary: "One class per page, so tests read like steps and change in one place."
updated: "2026-11-22"
---

# Page Object Model With Playwright and pytest

A **page object** is a class that knows one page: where its fields and buttons are, and how to do things on it. Tests use page objects instead of locators: `CartPage(page).open().remove("SQL in a Week")`. When the page changes, you fix one class, not fifty tests. And tests read like what a user does. This lesson walks through the template's framework and the rules that keep it clean.

!!! note "Before you start"
    Read [choosing locators](choosing-locators.md) and [waits](waits.md), and [fixtures and conftest](../pytest/fixtures-and-conftest.md). Have the [template project](index.md#templates) open.

## What you will learn

- What goes in a page object, and what stays in the test
- Components for parts that appear on many pages
- Methods that return the next page
- Fixtures that set up through the API, so tests start where they need to

## Why this matters at work

Without page objects, the locator for the **Remove** button is copied into every cart test. When a developer renames it, twenty tests fail and someone fixes twenty files. With page objects, the locator lives in one place. It's also the first thing interviewers ask about UI frameworks, and the first thing reviewers look for.

## The idea in plain words

!!! info "In plain words"
    A page object is a TV remote. You press "volume up". You don't open the TV and turn a dial inside it. If the maker changes the inside, the button still says "volume up". Tests press buttons on remotes; page objects know what's inside.

## Step by step

1. **Compare a test with and without page objects.** Both pass. Without:

    ```python
    def test_remove_without_page_objects(cart_with_books):
        page = cart_with_books
        page.goto("/cart")
        row = page.get_by_role("row").filter(has_text="SQL in a Week")
        row.get_by_role("button", name="Remove").click()
        expect(page.get_by_role("row").filter(has=page.get_by_role("cell"))).to_have_count(1)
        expect(page.get_by_test_id("cart-total")).to_have_text("24.99")
    ```

    With page objects, from `tests/test_cart.py`:

    ```python
    def test_remove_a_book_updates_the_total(cart_with_books):
        cart = CartPage(cart_with_books).open().remove("SQL in a Week")
        expect(cart.rows).to_have_count(1)
        expect(cart.total).to_have_text("24.99")
    ```

    The second says what happens. The first says how.

2. **Know the layout.**

    ```text
    ui_tests/
    ├── pages/                 # page objects: where things are, how to use them
    │   ├── __init__.py        # one import for all of them
    │   ├── header.py          # a component: on every page
    │   ├── login_page.py
    │   ├── books_page.py
    │   ├── cart_page.py
    │   └── checkout_page.py   # CheckoutPage and OrderPage
    ├── tests/                 # tests: what to do, what to expect
    │   ├── conftest.py        # browser, context, page, logged_in_page, cart_with_books
    │   └── test_*.py
    └── shop_app/              # the practice shop (delete it for your app)
    ```

3. **Read a page object.** `pages/cart_page.py`:

    ```python
    --8<-- "modules/core_automation/ui_automation/templates/ui_tests/pages/cart_page.py"
    ```

    - **Locators are made in `__init__`.** They are lazy, so making them early is free, and they're always up to date.
    - **Methods are things a user does:** `remove`, `empty_cart`, `go_to_checkout`. They take the words a test would use: a book title, not a row number.
    - **Methods return a page.** `remove()` returns `self`, so calls chain. `go_to_checkout()` returns a `CheckoutPage`, because that's where the user is now.
    - **`open()` goes to the page.** `BooksPage.open()` also waits until the list has loaded, as in [waits](waits.md).

4. **Use components for shared parts.** The header is on every page, so it's its own class, and each page has one: `cart.header.cart_count`. Change the header once, and every page gets it.

5. **Keep checks in the tests.** Page objects find and do. Tests check, with `expect()`. If a page object asserted "the total is right", a test reading `cart.remove(...)` wouldn't show that a check happens there, and the same method couldn't be used for a test that expects an error. The template's topic test fails if a page object contains `assert`. The one exception is waiting until a page is ready, which uses `expect()` to wait, not to check a result.

6. **Set up through the API.** Logging in through the form takes seconds, and only the log-in tests need to test it. From `tests/conftest.py`:

    ```python
    @pytest.fixture
    def logged_in_page(page):
        """Log in through the API: fast, and only the login tests need the login form.
        The page shares cookies with page.request, so the page is logged in too."""
        response = page.request.post("/api/login", data=TEST_USER)
        assert response.ok, response.text()
        return page


    @pytest.fixture
    def cart_with_books(logged_in_page):
        """Fill the cart through the API, then test the cart page itself."""
        for book in ["Python for Testers", "SQL in a Week", "SQL in a Week"]:
            assert logged_in_page.request.post("/api/cart", data={"book": book}).ok
        return logged_in_page
    ```

    `page.request` sends HTTP requests with the same cookies as the page. After the log-in request, the browser is logged in too. Every cart test starts on a full cart, with no clicking.

7. **Run them.**

    ```bash
    python -m pytest -v tests/test_checkout.py
    ```

    ```text
    tests/test_checkout.py::test_place_an_order PASSED                       [ 25%]
    tests/test_checkout.py::test_order_needs_the_terms_accepted PASSED       [ 50%]
    tests/test_checkout.py::test_card_number_must_have_16_digits PASSED      [ 75%]
    tests/test_checkout.py::test_terms_open_in_a_new_tab PASSED              [100%]
    ============================== 4 passed in 1.26s ===============================
    ```

    !!! success "Check: you should now be able to"
        Write a page object with locators and actions, return the next page from a method, share a header component, keep checks in tests, and set up through the API.

## When it goes wrong

- **Two pages import each other.** The header can go to the cart page, and the cart page has a header. With both imports at the top of the files:

    ```text
    E   ImportError: cannot import name 'Header' from partially initialized module 'pages.header' (most likely due to a circular import) (.../pages/header.py)
    ```

    The template imports the other page inside the method that needs it (`go_to_cart`, `go_to_checkout`), so the import happens later, when both files are loaded.
- **A test fails inside a page object method.** The traceback ends in `pages/...`. Read up to the test's line to see which step it was, then look at the screenshot. See [screenshots and traces](screenshots-and-traces.md).
- **A page object with 60 methods.** The page is doing too much, or the class holds several pages' worth. Split it into components: a search box, a results list, a filter panel.

## Common mistakes

!!! warning "Common mistakes"
    - **Asserts in page objects.** Tests stop showing what they check.
    - **Returning `None` from every method.** Tests can't chain, and lose track of which page they're on.
    - **One page object for the whole site.** Model pages and components the way the user sees them.
    - **Locators exposed as strings.** Keep them as `Locator` objects, so tests can use `expect()` on them.

!!! failure "If you see this error"
    **`AttributeError: 'CartPage' object has no attribute 'checkout'`**
    The test calls a method or locator the page object doesn't have, often an old name after a rename. Look at the class: here it's `checkout_link` or `go_to_checkout()`.

## Try it yourself

Add a `LoginPage` method `log_in_expecting_error(email, password)` that fills the form, clicks **Log in**, and returns the `LoginPage` itself (not `BooksPage`). Use it in `test_wrong_password_shows_an_error`.

??? success "Solution"
    ```python
    def log_in_expecting_error(self, email: str, password: str):
        self.email.fill(email)
        self.password.fill(password)
        self.log_in_button.click()
        return self
    ```

    ```python
    def test_wrong_password_shows_an_error(page):
        login = LoginPage(page).open().log_in_expecting_error(TEST_USER["email"], "wrong")
        expect(login.error).to_have_text("Wrong email or password")
    ```

    A wrong password keeps the user on the log-in page, so the method returns that page. The test still does the check.

## Quick check

1. What belongs in a page object, and what in a test?

    ??? question "Answer"
        Page objects: locators and actions. Tests: the steps and the checks with `expect()`.

2. Why does `go_to_checkout()` return a `CheckoutPage`?

    ??? question "Answer"
        After the click, the user is on the checkout page. The test continues with that page's actions.

3. Why log in through the API in most tests?

    ??? question "Answer"
        It's much faster, and the log-in form is already tested by the log-in tests.

## References

- [Martin Fowler: Page Object](https://martinfowler.com/bliki/PageObject.html)
- [Playwright: Page object models](https://playwright.dev/python/docs/pom)
- [Playwright: API testing (sharing cookies with the page)](https://playwright.dev/python/docs/api-testing)

Written for Python 3.13, pytest 9 and Playwright 1.64. Outputs captured November 2026. Links checked: November 2026.
