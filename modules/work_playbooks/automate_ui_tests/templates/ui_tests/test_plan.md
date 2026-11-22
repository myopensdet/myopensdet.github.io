<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->

# UI test plan: <feature or app name>

## 1. What and where

- Feature / ticket: <link to the story or ticket>
- Test site address: <https://test.example.com> (never production unless the team agrees in writing)
- Test users: <which users, with which roles; ask for test-only accounts>
- Test ids on elements: <data-testid / data-test / none yet: ask the developers>
- Browsers: <Chromium only / plus Firefox and WebKit>

## 2. User flows

| Flow | Steps a person takes | What they should see at the end |
| --- | --- | --- |
| Log in | Open the site, type user and password, press Login | The products page |
| Buy one product | Add to cart, open cart, checkout, fill the form, finish | "Thank you for your order!", empty cart |
| <your flow> | | |

## 3. Checks

| Kind | Check | Automated? |
| --- | --- | --- |
| Login | Right user gets in; wrong password and empty fields show a clear message | [ ] |
| Access | Pages need a login; logout really logs out | [ ] |
| Lists | Every item has a name, a price and its own picture; sorting sorts | [ ] |
| Numbers on screen | Cart count, totals = sum of items + tax | [ ] |
| Forms | Each required field shows its own error; typed values stay | [ ] |
| Main flow | The whole flow ends in the right place | [ ] |
| State | Cart kept after reload; nothing left from another test | [ ] |

## 4. Questions for the team

1. <Anything that looks odd, or a rule you can't find written down>

## 5. Not in this plan

- Business rules already covered by API tests (checked faster there)
- <Looks and layout: needs visual testing>
- <Speed: needs performance testing>
