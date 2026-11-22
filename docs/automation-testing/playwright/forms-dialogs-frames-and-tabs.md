---
title: "Forms, Dialogs, Iframes and New Tabs in Playwright"
description: "Automate the tricky parts of a checkout with Playwright for Python: text fields, selects, radio buttons and checkboxes; confirm and alert dialogs; a card field inside an iframe; and a link that opens a new tab."
level: Intermediate
tags:
  - Playwright
  - UI
nav_title: "Forms, dialogs, frames and tabs"
order: 50
summary: "Selects, radios, checkboxes, confirm dialogs, iframes and new tabs."
updated: "2026-11-22"
---

# Forms, Dialogs, Iframes and New Tabs in Playwright

A checkout page has everything that makes UI tests hard. It has a form with a dropdown and radio buttons. The card field lives inside an **iframe**: another page shown inside this one. The terms link opens a **new tab**. And the cart page asks a **confirm dialog** before it empties the cart. Each needs one specific move in Playwright. Without it, the test waits and times out, or does nothing and fails later.

!!! note "Before you start"
    Read [Page Object Model](page-object-model.md). Have the [template project](index.md#templates) open.

## What you will learn

- How to fill text fields, choose from a select, and check radio buttons and checkboxes
- How to answer confirm and alert dialogs
- How to reach a field inside an iframe
- How to catch a new tab and check it

## Why this matters at work

Payment forms are almost always in an iframe from the payment provider. "Are you sure?" dialogs guard every delete. Terms, help and invoices open in new tabs. UI suites often fail at these steps with a timeout, and nobody knows why. Each one needs one move, and this page shows it.

## The idea in plain words

!!! info "In plain words"
    An iframe is a picture frame on the wall with another room's window in it: to touch something in there, you first reach through the frame. A dialog is a doorbell: someone must answer it, or it's ignored. A new tab is a second door that opens: you have to notice it opened, then walk through.

## Step by step

1. **Read the checkout page object.** `pages/checkout_page.py`:

    ```python
    --8<-- "modules/core_automation/ui_automation/templates/ui_tests/pages/checkout_page.py"
    ```

2. **Fill the form.**

    | Field | Playwright | In the template |
    | --- | --- | --- |
    | Text | `fill(text)` | `self.full_name.fill(name)` |
    | Select (dropdown) | `select_option(label or value)` | `self.country.select_option(country)` |
    | Radio button | `check()` on the one you want | `get_by_role("radio", name=delivery).check()` |
    | Checkbox | `check()` or `uncheck()` | `self.terms.check()` |
    | File upload | `set_input_files(path)` | Not in this shop. See the references |

    `fill()` replaces what's in the field. `check()` makes sure it ends up checked, so calling it twice is safe, unlike `click()`.

3. **Reach into the iframe.** The card field is in its own page, `/payment-frame`, shown in an `<iframe title="Payment">`. A normal locator only searches the main page. `frame_locator()` searches inside the frame:

    ```python
    self.card_number = page.frame_locator("iframe[title=Payment]").get_by_label("Card number")
    ```

    After that, `self.card_number.fill(card)` works like any field.

4. **Answer the dialog.** **Empty cart** opens the browser's own confirm dialog, `Empty your cart?`, with OK and Cancel. Tell Playwright the answer *before* you click:

    ```python
    def empty_cart(self, *, confirm: bool):
        """Click "Empty cart" and answer the browser's confirm dialog with OK or Cancel."""
        self.page.once("dialog", lambda dialog: dialog.accept() if confirm else dialog.dismiss())
        self.empty_button.click()
        return self
    ```

    `once` handles only the next dialog, so it can't answer one you didn't expect later. Two tests cover both answers: OK empties the cart, Cancel keeps the 2 rows.

5. **Catch the new tab.** The terms link has `target="_blank"`. Wrap the click in `expect_page()`, and you get the new tab:

    ```python
    def open_terms(self) -> Page:
        """The link opens a new tab. Wait for it, and hand it back for checks."""
        with self.page.context.expect_page() as new_tab:
            self.terms_link.click()
        return new_tab.value
    ```

    The test checks the new tab's heading, then that the checkout tab is still there:

    ```python
    def test_terms_open_in_a_new_tab(checkout):
        terms = checkout.open_terms()
        expect(terms.get_by_role("heading", name="Terms of sale")).to_be_visible()
        expect(checkout.place_order_button).to_be_visible()  # the checkout tab is still there
    ```

6. **Put it together.** The whole checkout, from `tests/test_checkout.py`:

    ```python
    --8<-- "modules/core_automation/ui_automation/templates/ui_tests/tests/test_checkout.py"
    ```

    68.98 is the cart (63.99) plus express delivery (4.99).

    !!! success "Check: you should now be able to"
        Fill text fields, selects, radios and checkboxes; answer a confirm dialog both ways; fill a field inside an iframe; and check a page opened in a new tab.

## When it goes wrong

- **The dialog wasn't answered.** With no handler, Playwright dismisses dialogs by itself: the same as clicking Cancel. The cart stays full, and the next check fails, far from the cause:

    ```text
    E       AssertionError: Locator expected to be visible
    E       Actual value: None
    E       Error: element(s) not found
    E       Call log:
    E         - Expect "to_be_visible" get_by_text("Your cart is empty.") with timeout 5000ms
    ```

    The page snapshot under it still shows both rows. Add a `dialog` handler before the click.
- **The field is in an iframe.** `page.get_by_label("Card number")` searches the main page only, so it waits and gives up (this run used a 3-second timeout):

    ```text
    E           playwright._impl._errors.TimeoutError: Locator.fill: Timeout 3000ms exceeded.
    E           Call log:
    E             - waiting for get_by_label("Card number")
    ```

    If you can see a field but Playwright can't find it, look for an `<iframe>` around it in the browser's developer tools.
- **The new tab was ignored.** Clicking the link and then looking on the same page finds nothing:

    ```text
    E       AssertionError: Locator expected to be visible
    E       Actual value: None
    E       Error: element(s) not found
    E       Call log:
    E         - Expect "to_be_visible" get_by_role("heading", name="Terms of sale") with timeout 5000ms
    ```

    The heading is in the other tab. Use `expect_page()` around the click.
- **The option isn't in the select.** `select_option("France")` when the list has no France waits, then times out, and its call log says `did not find some options`.

## Common mistakes

!!! warning "Common mistakes"
    - **Setting the dialog handler after the click.** The dialog is already gone. Handler first, then click.
    - **`click()` on a checkbox to tick it.** If it's already ticked, that unticks it. Use `check()`.
    - **Real card numbers in tests.** Use the test card numbers your payment provider publishes, never a real one.
    - **Switching to the new tab and forgetting the old one.** Both are open; check the one you mean.

!!! failure "If you see this error"
    **`Locator.select_option: Timeout 3000ms exceeded.`** with **`did not find some options`** in the call log
    The text you asked for isn't one of the options. Compare it with the option labels on the page, or use the option's `value`.

## Try it yourself

Write a test that clicks **Empty cart**, answers Cancel, and checks the dialog's message was `Empty your cart?`.

??? success "Solution"
    ```python
    def test_empty_cart_dialog_asks_the_right_question(cart_with_books):
        cart = CartPage(cart_with_books).open()
        messages = []

        def answer(dialog):
            messages.append(dialog.message)
            dialog.dismiss()

        cart_with_books.once("dialog", answer)
        cart.empty_button.click()
        expect(cart.rows).to_have_count(2)
        assert messages == ["Empty your cart?"]
    ```

    `dialog.message` is the dialog's text; `dialog.type` is `confirm` here. `click()` returns only after the dialog has been answered, so `messages` is filled by the last line.

## References

- [Playwright: Actions (fill, select, check, upload)](https://playwright.dev/python/docs/input)
- [Playwright: Dialogs](https://playwright.dev/python/docs/dialogs)
- [Playwright: Frames](https://playwright.dev/python/docs/frames)
- [Playwright: Pages and new tabs](https://playwright.dev/python/docs/pages)

Written for Python 3.13 and Playwright 1.64. Outputs captured November 2026. Links checked: November 2026.
