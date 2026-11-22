<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Test summary: <release or feature name>

Date: <YYYY-MM-DD>   Tester(s): <names>   Build: <version>

## Verdict

**<GREEN / AMBER / RED>**: <one sentence: ready, ready if you accept the risks, or not ready, and why>

## What we tested

| Area | How | Result |
| --- | --- | --- |
| <area> | <automated N tests / exploratory / smoke only> | <pass / N bugs> |

## What we did NOT test, and why

- <area>: <reason: no data, no environment, out of scope, no time>

## Bugs

| Ticket | What | Severity | Status |
| --- | --- | --- | --- |
| <ID> | <one line> | <high/medium/low> | <open / fixed / won't fix> |

## Risks for the release

| Risk | Who it affects | How likely | What we suggest |
| --- | --- | --- | --- |
| <risk> | <users> | <often / rare> | <release anyway / wait / feature flag off> |

## Numbers

- Automated tests: <passed>/<total> passed
- Bugs found: <N> (<N> fixed, <N> open)
