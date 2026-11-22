<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Playwright locators cheat sheet (Python)

Every line here runs in `test_locators.py`, on `locator_practice.html`. Pick from the top of the first table down: the higher, the closer to what a user sees, and the less it breaks.

## Find an element

| Find by | Write | Use when |
| --- | --- | --- |
| Role and name | `page.get_by_role("button", name="Save")` | **First choice.** Buttons, links, headings, fields, checkboxes |
| Heading | `page.get_by_role("heading", name="Practice shop")` | Checking you're on the right page |
| Link | `page.get_by_role("link", name="Help")` | Menus and links |
| Checkbox | `page.get_by_role("checkbox", name="Send me news")` | Checkboxes and radio buttons (`"radio"`) |
| Label | `page.get_by_label("Email")` | Form fields with a label |
| Placeholder | `page.get_by_placeholder("you@example.com")` | Fields with no label (ask for a label: it's an accessibility bug) |
| Text | `page.get_by_text("Last saved")` | Text that isn't a button or link |
| Image text | `page.get_by_alt_text("Shop logo")` | Images |
| Title | `page.get_by_title("Saved at 10:00")` | Elements with a tooltip title |
| Test id | `page.get_by_test_id("save-button")` | Nothing else is stable. Ask developers for `data-testid` |
| CSS | `page.locator(".product .price")` | Last choice. Classes change when the design changes |

`get_by_text` and `name=` match **part** of the text, ignoring case. Add `exact=True` for the whole text: `page.get_by_text("Last saved: today", exact=True)`.

## Narrow it down

| You want | Write |
| --- | --- |
| The row that has some text | `page.get_by_role("listitem").filter(has_text="Test mug")` |
| A button inside that row | `page.get_by_role("listitem").filter(has_text="Test mug").get_by_role("button", name="Add to cart")` |
| Rows that contain an element | `page.locator(".product").filter(has=page.get_by_role("button", name="Sold out"))` |
| A name that starts with some text | `page.get_by_role("link", name=re.compile(r"^Cart"))` |
| First, last, by position (from 0) | `page.locator(".price").first`, `.last`, `.nth(1)` |

Use `first` and `nth` only when the order **is** the test ("the newest order is on top"). Otherwise filter by text: it doesn't break when the order changes.

## Act

| Do | Write |
| --- | --- |
| Click | `page.get_by_test_id("save-button").click()` |
| Type into a field (clears it first) | `page.get_by_label("Email").fill("arshad.test@example.com")` |
| Tick a checkbox | `page.get_by_role("checkbox", name="Send me news").check()` |
| Pick from a list | `page.get_by_label("Country").select_option("United Kingdom")` |
| Press a key | `page.get_by_label("Email").press("Enter")` |

Playwright waits for the element to be visible and enabled before it acts. No `sleep()` needed.

## Check (`from playwright.sync_api import expect`)

| Check | Write |
| --- | --- |
| It's visible | `expect(page.get_by_role("alert")).to_be_visible()` |
| Exact text | `expect(page.get_by_role("heading", name="Practice shop")).to_have_text("Practice shop")` |
| Contains text | `expect(page.get_by_title("Saved at 10:00")).to_contain_text("today")` |
| How many | `expect(page.locator(".product")).to_have_count(3)` |
| A field's value | `expect(page.get_by_label("Email")).to_have_value("arshad.test@example.com")` |
| Ticked | `expect(page.get_by_role("checkbox", name="Send me news")).to_be_checked()` |
| Disabled | `expect(page.get_by_role("button", name="Sold out")).to_be_disabled()` |
| An attribute | `expect(page.get_by_label("Email")).to_have_attribute("type", "email")` |
| The page title | `expect(page).to_have_title("Locator practice")` |
| The address | `expect(page).to_have_url(re.compile(r"/orders/\d+"))` |

`expect` checks again and again for up to 5 seconds, so it works with pages that load slowly. Plain `assert locator.is_visible()` checks once, and fails on slow pages.

## Find a locator fast

- `playwright codegen https://your-app.example.com`: click around, and it writes the locators.
- In a failing test, the error shows what Playwright found. `page.pause()` opens the inspector.
