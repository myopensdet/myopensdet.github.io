<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Test strategy: <team or product>

Owner: <who keeps this up to date> · Last reviewed: <YYYY-MM-DD> · Review again: <every 6 months, or after a big change>

One page for the whole team. It says how we test, every time. Each feature's test plan follows it.

## 1. What we protect most

The two or three things that must never break, in the users' words.

-

## 2. Test levels: who tests what, and when

| Level | What it checks | Who writes it | Tools | Runs when |
| --- | --- | --- | --- | --- |
| Unit | <rules and calculations> | <developers> | <pytest> | <every push> |
| API | <each endpoint, errors, auth> | <developers and SDETs> | <pytest, requests> | <every pull request> |
| UI (end to end) | <a few key journeys> | <SDETs> | <Playwright> | <every pull request, or nightly> |
| Manual and exploratory | <new features, looks, feel> | <testers> | <charters, checklists> | <each story> |

## 3. What we automate, and what we don't

- Automate: <checks that run often, give the same result every time, and protect section 1>
- Keep manual: <looks and feel, one-off checks, features still changing every week>
- Decide with: the automation checklist and the payback calculator.

## 4. Environments and test data

| Environment | Used for | Data |
| --- | --- | --- |
| <local> | <unit and API tests> | <made by the tests, deleted after> |
| <staging> | <end-to-end and exploratory> | <test accounts only, never real customers> |

## 5. Bugs

- Where: <tracker>, using the bug report form.
- Severity and priority: <link to the team's guide>.
- Every fixed bug gets a test that would have caught it.

## 6. When a feature is ready to release

The default exit criteria. A test plan can make them stricter, never looser without a written reason.

- No failing automated tests on the release build
- No open critical bugs, and no open major bugs without a written reason
- Every requirement has at least one test
- Every high risk has been tested

## 7. How we report

- <a test summary per release, shared in <channel>>
- <the pipeline result on every pull request>
