<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Test plan: refund requests (release 2.4)

Author: QA engineer · Reviewed by: lead, refund developer, product owner · Date: 2026-11-16
Follows: the shop's test strategy · Story: "Refund an item from My orders" (REF-1 to REF-7)

## 1. What and why

Customers can now ask for a refund themselves, from My orders. If it breaks, money goes out twice or to the wrong place, or customers flood support.

## 2. Scope

| In scope | Out of scope (and why) |
| --- | --- |
| The refund rules REF-1 to REF-7 | Partial refunds (not in this release) |
| The refund page, in English and Bengali | The support team's refund tool (unchanged) |
| Approval and refusal emails | The payment provider itself (tested by them; we test our calls to it) |

## 3. Risks, highest first

| Score | Depth | Area | Risk |
| --- | --- | --- | --- |
| 6 | deep | Money | The same item is refunded twice (REF-2) |
| 6 | deep | Money | Money goes back to the wrong place (REF-5) |
| 6 | deep | Rules | Day 30 or day 31 is handled wrongly (REF-1) |
| 4 | normal | Email | The approval or refusal email is not sent (REF-3) |
| 4 | normal | Rules | A sale item is refunded when it is not faulty (REF-4) |
| 3 | normal | Money | A refund to an expired card is lost (REF-6) |
| 2 | light | Page | Long Bengali item names break the refund page layout |
| 1 | light | Page | The Cancel order link is missing for undelivered orders (REF-7) |

## 4. Approach

| What | How | Level | Automated? |
| --- | --- | --- | --- |
| REF-1 day limit | Boundary values: days 0, 30, 31 | Unit | Yes |
| REF-2 refunded twice | Negative case, plus two refunds at the same moment | Unit and API | Yes |
| REF-5 where money goes | One case per payment type | Unit and API | Yes |
| REF-3 emails | Check the email arrives and says the right thing | Manual | No: wording needs a human eye |
| Bengali layout | Exploratory charter, 30 minutes, phone and laptop | Manual | No: looks can't be asserted well |
| Refund journey | Log in, refund an item, see the status | UI | Yes, one test |

## 5. Entry criteria: we start testing when

- [x] The story has been reviewed, and open questions have answers
- [x] The build is on staging, and its version is known
- [x] Test accounts with delivered, sale and undelivered orders are ready
- [x] The payment sandbox accepts refunds to card, PayPal and gift card

## 6. Exit criteria: testing is done when

Kept in `refund_exit_criteria.toml` and checked with `exit_check.py`.

- [ ] No failing automated tests on the release build
- [ ] No open critical bugs, and no open major bugs
- [ ] Every requirement has at least one test (traceability report)
- [ ] Every deep risk has been tested

## 7. Environments, data and access

Staging, with the payment sandbox. Test accounts only. Access to the email test inbox is still needed.

## 8. Who and when

| Task | Who | By |
| --- | --- | --- |
| Unit and API tests | Refund developer, reviewed by SDET | Wednesday |
| UI journey test | SDET | Thursday |
| Emails and Bengali layout | QA engineer | Thursday |
| Exit check and test summary | QA engineer | Friday morning |

## 9. What you will share

- The test summary, with the exit check output, in the team channel
- Bug reports, linked from the summary

## 10. Open questions

- Two refunds at the same moment: should the second one fail with a message, or wait? (asked the product owner)
