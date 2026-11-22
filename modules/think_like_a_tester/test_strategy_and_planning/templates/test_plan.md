<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Test plan: <feature> (<release>)

Author: <your name> · Reviewed by: <lead, developer, product owner> · Date: <YYYY-MM-DD>
Follows: <link to the team's test strategy> · Story: <link>

## 1. What and why

One or two sentences: what changes in this release, and what would hurt if it broke.

## 2. Scope

| In scope | Out of scope (and why) |
| --- | --- |
|  |  |

## 3. Risks, highest first

Paste the output of `risk_score.py`. Deep risks get the most tests, light ones a quick look.

| Score | Depth | Area | Risk |
| --- | --- | --- | --- |
|  |  |  |  |

## 4. Approach

| What | How | Level | Automated? |
| --- | --- | --- | --- |
| <risk or requirement> | <technique: boundary values, negative cases...> | <unit, API, UI, manual> | <yes / no, and why> |

## 5. Entry criteria: we start testing when

- [ ] The story has been reviewed, and open questions have answers
- [ ] The build is on <environment>, and its version is known
- [ ] Test data and accounts are ready
- [ ] <anything else this feature needs, like a payment sandbox>

## 6. Exit criteria: testing is done when

Kept in `exit_criteria.toml` and checked with `exit_check.py`.

- [ ] No failing automated tests on the release build
- [ ] No open critical bugs, and no open major bugs
- [ ] Every requirement has at least one test (traceability report)
- [ ] Every deep risk has been tested

## 7. Environments, data and access

<where you test, which accounts, what access you still need>

## 8. Who and when

| Task | Who | By |
| --- | --- | --- |
|  |  |  |

## 9. What you will share

- <the test summary, with the exit check output>
- <bug reports, linked from the summary>

## 10. Open questions

-
