<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->

# Speed check plan: <app or release name>

## 1. Where and when

- Environment: <test or staging address> (never production without written approval)
- Who agreed: <name of the person who owns that environment>
- When: <date and time; tell the team before you start>
- How to stop it: Ctrl+C in the terminal. Who to call if it breaks: <name>

## 2. Targets

| Page | Users at once | p95 under | Errors under | Where the number comes from |
| --- | --- | --- | --- | --- |
| <GET /api/products> | <10> | <300 ms> | <1%> | <ticket, SLA, or "today's speed + 20%"> |
| <GET /api/search?q=...> | | | | |

## 3. Steps

1. One user on each page: the baseline.
2. The agreed number of users on each page.
3. Anything over target: run again, then report with both numbers.

## 4. Results

| Page | 1 user p95 | N users p95 | Errors | Target met? |
| --- | --- | --- | --- | --- |
| | | | | |

## 5. Questions for the team

1. <Where do the targets come from? How many users at once is normal, and at the busiest hour?>

## 6. Not in this plan

- Long runs (hours) and finding the breaking point: a load testing tool such as Locust or k6
- Page load in the browser: browser tools (Lighthouse)
