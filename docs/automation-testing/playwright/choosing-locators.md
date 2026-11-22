---
title: "Choosing Locators in Playwright: Role, Label, Test Id, Then CSS"
description: "Pick locators that survive page changes: get_by_role and get_by_label first, get_by_text, then data-testid, and CSS or XPath only as a last resort. Narrow locators to a row or card with filter() and chaining, instead of nth()."
level: Intermediate
tags:
  - Playwright
  - UI
nav_title: "Choosing locators"
order: 20
summary: "Find things like a user: role and label first, test id next, CSS last."
updated: "2026-11-22"
---

# Choosing Locators in Playwright: Role, Label, Test Id, Then CSS

A **locator** is how a test finds something on the page. A good one finds exactly the right element, still works after a redesign, and tells the reader what it is. Playwright's advice, and this site's, is to find things the way a user does: "the **Log in** button", "the **Email** field". Only when that's not possible, use a test id the developers add for you. CSS and XPath come last.

!!! note "Before you start"
    Read [how browsers and locators work](how-browsers-and-locators-work.md). Have the [template project](index.md#templates) open.

## What you will learn

- Which locator to choose, in order
- How to narrow a locator to one row or card
- When a test id is the right answer, and what CSS and XPath cost you

## Why this matters at work

Most UI test maintenance is fixing locators after a page changed. `//div[3]/div[2]/button` breaks when a designer adds a wrapper `div`. "The **Remove** button in the **SQL in a Week** row" only breaks when the feature really changes. Good locators also check something real: a button a screen reader can't name is a bug.

## The idea in plain words

!!! info "In plain words"
    Telling a friend where your keys are, you say "on the kitchen table, next to the fruit bowl". Not "1.2 metres from the north wall, 80 centimetres up". The first still works after you move the furniture. Good locators are the first kind.

## Step by step

1. **Choose in this order.**

    | Choice | Example | Use it for |
    | --- | --- | --- |
    | 1. Role and name | `get_by_role("button", name="Log in")` | Buttons, links, headings, checkboxes, rows: most things |
    | 2. Label | `get_by_label("Email")` | Form fields with a label |
    | 3. Text | `get_by_text("Your cart is empty.")` | Messages and plain text |
    | 4. Test id | `get_by_test_id("cart-count")` | Things with no role or label, like a number in a badge |
    | 5. CSS or XPath | `locator("#email")` | Last resort, when nothing above works |

    There are also `get_by_placeholder`, `get_by_alt_text` (images) and `get_by_title`, used the same way.

2. **Read the template's page objects with that order in mind.** The log-in page uses only roles and labels:

    ```python
    --8<-- "modules/core_automation/ui_automation/templates/ui_tests/pages/login_page.py"
    ```

    The header needs a test id for the count: it's a plain number with no role or label. The page has `<span data-testid="cart-count">3</span>`.

    ```python
    --8<-- "modules/core_automation/ui_automation/templates/ui_tests/pages/header.py"
    ```

    The `nav` locator is used to narrow the others: "the **Cart** link *in the main navigation*", not any **Cart** link on the page.

3. **Know how names match.** By default, `name=` ignores case and matches part of the name: `name="log"` finds the **Log in** button. Add `exact=True` to match the whole name exactly:

    ```python
    page.get_by_role("button", name="log").count()              # 1
    page.get_by_role("button", name="log", exact=True).count()  # 0
    ```

    Part-matching is usually what you want. Use `exact=True` when two names start the same, like **Save** and **Save as**.

4. **Narrow to one row or card.** Every book card has an **Add to cart** button. Asking for "the **Add to cart** button" matches four:

    ```text
    playwright._impl._errors.Error: Locator.click: Error: strict mode violation: get_by_role("button", name="Add to cart") resolved to 4 elements:
        1) <button>Add to cart</button> aka get_by_role("listitem").filter(has_text="Python for TestersPrice: 24.").get_by_role("button")
        2) <button>Add to cart</button> aka get_by_role("listitem").filter(has_text="SQL in a WeekPrice: 19.50Add").get_by_role("button")
        3) <button>Add to cart</button> aka get_by_role("listitem").filter(has_text="Clean TestsPrice: 31.00Add to").get_by_role("button")
        4) <button>Add to cart</button> aka get_by_role("listitem").filter(has_text="Playwright Pocket GuidePrice").get_by_role("button")
    ```

    So find the card first, then the button inside it. From `pages/books_page.py`:

    ```python
    def book(self, title: str) -> Locator:
        """The card of one book: every card has an "Add to cart" button, so find the card first."""
        return self.results.filter(has=self.page.get_by_role("heading", name=title))

    def add_to_cart(self, title: str):
        self.book(title).get_by_role("button", name="Add to cart").click()
        return self
    ```

    - `filter(has=...)` keeps only the cards that contain that heading.
    - `filter(has_text=...)` keeps the ones whose text contains the words. The cart page uses it for rows: `self.rows.filter(has_text=title)`.
    - Chaining, `card.get_by_role(...)`, searches only inside the card.

5. **Avoid position.** `get_by_role("button", name="Add to cart").nth(1)` clicks the second card's button. Today that's **SQL in a Week**. After someone sorts the list by price, it's another book, and the test still passes while it checks the wrong thing. Use `nth()` and `first` only when the position *is* what you test, like "the newest order is at the top".

6. **Ask for test ids when you need them.** If something has no role, label or useful text, ask developers to add `data-testid="..."`. It's a contract: a name that exists only for tests, and that nobody changes for design reasons. In the template, the cart count, the cart total and the order number have one.

7. **Let Playwright suggest one.** `python -m playwright codegen http://127.0.0.1:8080` opens a browser and a recorder window (use your app's address). Click something, and it writes the locator it would use, usually by role. Use its suggestions as a start, then put them in page objects.

    !!! success "Check: you should now be able to"
        Pick a locator in the right order, narrow it to one row or card with `filter()`, and explain why `nth()` and long CSS paths are risky.

## When it goes wrong

- **A label with a typo.** `get_by_label("E-mail")` when the label says **Email**:

    ```text
    playwright._impl._errors.TimeoutError: Locator.fill: Timeout 10000ms exceeded.
    Call log:
      - waiting for get_by_label("E-mail")
    ```

    Playwright waited 10 seconds (the template's timeout) for a field that never matched. When a locator times out, compare its words with the page, letter by letter.
- **`strict mode violation`.** More than one match. Narrow with a row, card or section, as in step 4. The error's `aka` lines suggest locators for each match.
- **A button has no name.** An icon-only button with no text or `aria-label` can't be found by role and name, and a screen reader can't name it either. Report it as an accessibility bug, and use a test id until it's fixed.

## Common mistakes

!!! warning "Common mistakes"
    - **Copying the long XPath from the browser's "Copy XPath".** `/html/body/main/ul/li[2]/button` breaks with any layout change.
    - **Locating by CSS classes.** `.btn-primary` is about looks. Designers change it.
    - **Using `nth()` to fix strict mode errors.** The test passes and checks the wrong row. Narrow by content instead.
    - **Text that changes.** `get_by_text("3 books")` breaks when there are 4. Locate the element, then check its text with `expect()`.

!!! failure "If you see this error"
    **`Error: strict mode violation: get_by_text("Price") resolved to 4 elements:`** (then `<p>Price: 24.99</p>` and the other three)
    `get_by_text` matches part of the text by default, so "Price" matches every price on the page. Narrow it to the card first, or use `exact=True` with the full text.

## Try it yourself

Write a check that the card of **Clean Tests** shows `Price: 31.00`, using `BooksPage`.

??? success "Solution"
    ```python
    def test_clean_tests_price(logged_in_page):
        books = BooksPage(logged_in_page).open()
        expect(books.book("Clean Tests").get_by_text("Price:")).to_have_text("Price: 31.00")
    ```

    `book("Clean Tests")` narrows to one card, so `get_by_text("Price:")` finds exactly one element.

## References

- [Playwright: Locators](https://playwright.dev/python/docs/locators)
- [Playwright: Filtering locators](https://playwright.dev/python/docs/locators#filtering-locators)
- [Playwright: Test generator (codegen)](https://playwright.dev/python/docs/codegen)
- [Testing Library: Which query should I use?](https://testing-library.com/docs/queries/about/#priority)
- [MDN: ARIA roles](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles)

Written for Python 3.13 and Playwright 1.64. Outputs captured November 2026. Links checked: November 2026.
