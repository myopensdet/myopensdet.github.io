<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Test strategy: the example shop

Owner: QA engineer · Last reviewed: 2026-11-16 · Review again: May 2027, or when we add a new payment type

## 1. What we protect most

- Customers can pay, and are charged the right amount, once.
- Refunds go to the right place, once.
- Customers can sign up and log in with their own name, in English or Bengali.

## 2. Test levels: who tests what, and when

| Level | What it checks | Who writes it | Tools | Runs when |
| --- | --- | --- | --- | --- |
| Unit | Prices, delivery fees, refund and sign-up rules | Developers, with SDET review | pytest | Every push |
| API | Each endpoint: right answers, errors, login | Developers and SDETs | pytest, requests | Every pull request |
| UI (end to end) | Sign up, buy, refund: three journeys only | SDETs | Playwright | Every pull request |
| Manual and exploratory | New features, layout in Bengali, emails | Testers | Charters, checklists | Each story |

## 3. What we automate, and what we don't

- Automate: every money rule (unit), every endpoint (API), the three main journeys (UI).
- Keep manual: how pages look in Bengali and on small phones, email wording, one-off data fixes.
- Decide with: the automation checklist and the payback calculator.

## 4. Environments and test data

| Environment | Used for | Data |
| --- | --- | --- |
| Local | Unit and API tests | Made by the tests, deleted after |
| Staging | End-to-end and exploratory | Test accounts only, reset every night |

## 5. Bugs

- Where: GitHub issues, using the bug report form.
- Severity and priority: the team's severity guide.
- Every fixed bug gets a test that would have caught it.

## 6. When a feature is ready to release

- No failing automated tests on the release build
- No open critical bugs, and no open major bugs without a written reason
- Every requirement has at least one test
- Every high risk has been tested

## 7. How we report

- A one-page test summary per release, with the exit check output, shared in the team channel.
- The pipeline result on every pull request.
