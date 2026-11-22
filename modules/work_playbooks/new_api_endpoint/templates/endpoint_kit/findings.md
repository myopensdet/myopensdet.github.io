<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Test results: `POST /carts/add`

**Tested on:** staging, build `...`, on `YYYY-MM-DD`
**Tested by:** your name
**How:** 12 probe cases (`api_probe.py`, cases in `cases.json`) and 8 automated checks
(`tests/test_endpoint.py`: 4 passed, 4 failed).

## Summary

The happy path works. Bad input is mostly accepted: negative and text quantities and unknown
products give `201 Created` with wrong or empty carts. **Not ready to release** until the
first two are fixed.

## Bugs

| # | What | Severity | Ticket |
| --- | --- | --- | --- |
| 1 | Negative quantity accepted: `quantity: -2` gives `201` and `total: -89.98` | High | ? |
| 2 | Text quantity accepted: `quantity: "many"` gives `201` with `quantity`, `total` = `null` | High | ? |
| 3 | Unknown product silently dropped: `id: 99999` gives `201` with an empty cart | Medium | ? |
| 4 | `quantity: 0` silently changed to 1 | Medium, or as designed? | ? |

## Questions still open

1. Largest allowed quantity? `1000000` was accepted (`total: 44990000`).
2. Same product twice is merged into one line (quantity 2). Intended?

## Not tested

Access rules (no test token yet), database side effects (no database access yet), speed under load.

## How to run the checks again

    BASE_URL=https://staging... API_TOKEN=... python -m pytest
