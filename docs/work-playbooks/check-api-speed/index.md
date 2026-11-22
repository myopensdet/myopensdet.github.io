---
title: "How to Check API Speed Under Load, Step by Step"
description: "A step-by-step guide to a first performance check at work: agree on targets, measure one user, then many users at once, and read p50, p95 and errors. Copy a ready Python speed-check script and pytest speed tests, find slow and failing pages, and fix the common errors."
level: Beginner
tags:
  - Performance
  - API
  - Templates
nav_title: "Check API speed, step by step"
order: 50
group: "Speed"
summary: "Targets, one user, many users, read p95 and errors, speed tests in pytest."
updated: "2026-11-22"
---

# How to Check API Speed Under Load, Step by Step

"Is it fast enough?" sounds simple. It isn't, because a page that answers in 50 ms for you can take half a second, or fail, when ten people use it at once. This guide takes you from nothing to a repeatable speed check: what to agree first, how to measure, how to read the numbers, and ready scripts to copy. Follow the steps in order.

!!! example "The situation"
    **Your lead:** "Marketing is sending a newsletter on Monday. Can you check the shop API holds up when lots of people come at once?"

You'll practise on a **small practice API** that runs on your own computer, with two speed problems of the kind real apps ship. Never practise on a public site: load you send costs its owner money and can take it down for everyone.

!!! danger "Only load what you're allowed to load"
    A speed check sends thousands of requests. Run it only on a test environment, only with the owner's OK, and tell the team before you start. Never on production without written approval: you can take the real site down.

## Step 1: Install what you need

You need **Python 3.13** and **VS Code**. If you don't have them, follow [environment setup](../../start-here/environment-setup/index.md) first.

1. **Get the files**: copy them from [Templates](#templates) below into a new folder, or take the whole folder [from GitHub](https://github.com/arshaduzzaman-sm/myopensdet/tree/main/modules/work_playbooks/check_api_speed/templates). Then open the `speed_check` folder in VS Code (**File → Open Folder**).

2. **Open a terminal** in VS Code (**Terminal → New Terminal**), make a virtual environment and install pytest and requests:

    === "macOS / Linux"

        ```bash
        python3.13 -m venv .venv
        source .venv/bin/activate
        python -m pip install -r requirements.txt
        ```

    === "Windows"

        ```powershell
        py -3.13 -m venv .venv
        .venv\Scripts\Activate.ps1
        python -m pip install -r requirements.txt
        ```

3. **Start the practice API** in this terminal. It needs no packages, and only your computer can reach it:

    ```bash
    python practice_api.py
    ```

    ```text
    Practice API (with planted speed problems) on http://127.0.0.1:8770  (Ctrl+C to stop)
    ```

    Leave it running. Open a **second terminal** (the **+** in the terminal panel) and activate `.venv` there too.

## Step 2: Agree on the targets first

A speed check without a target ends in "is 400 ms good?" and nobody knows. **Get three numbers per page before you measure:**

| Ask | Why | Example |
| --- | --- | --- |
| **How many users at once?** | Normal day, and the busiest hour. Not "visitors per day" | 10 at once on Monday morning |
| **How fast?** As **p95**: 95 of 100 answers must be faster than this | An average hides the slow ones. p95 is what unlucky users feel | p95 under 300 ms |
| **How many errors are OK?** | Under load, the first thing to break is often "error" answers, not speed | Under 1% |

No numbers anywhere? Measure today's speed (step 4) and propose "no worse than today, plus 20%". Write down who agreed.

**The words you'll see:**

| Word | Means |
| --- | --- |
| **p50** | Half the answers were faster than this. A normal answer |
| **p95** | 95% were faster. The usual target |
| **p99** | 99% were faster. The slowest 1 in 100 |
| **Requests per second** | How much work the system did |
| **Users at once** | Here: each "user" sends a request, waits for the answer, then sends the next |

## Step 3: Pick the pages, and write the plan

Not every page needs a speed check. Pick:

- **The busiest pages**: the home page list, search, product details.
- **The heavy ones**: reports, exports, anything that adds up a lot of data.
- **What changed** in this release.

Copy `test_plan.md` from the project and fill it in. The targets table is the heart of it:

```markdown
| Page | Users at once | p95 under | Errors under | Where the number comes from |
| --- | --- | --- | --- | --- |
| GET /api/products | 10 | 300 ms | 1% | today's speed + 20% |
| GET /api/search?q=book | 10 | 300 ms | 1% | same as products |
| GET /api/report | 10 | 1000 ms | 1% | ticket SHOP-88 |
```

The plan also says **where, when, who agreed, and who to call** if something breaks. Post it in the ticket before you run anything.

## Step 4: Measure one user first

The project has `speed_check.py`: it sends requests from many "users" at once and prints the numbers. It only needs Python and requests:

```python
--8<-- "modules/work_playbooks/check_api_speed/templates/speed_check/speed_check.py"
```

**Start with one user.** That's the baseline: how fast each page is when nobody else is using it. In the second terminal:

```bash
python speed_check.py http://127.0.0.1:8770/api/products --users 1 --seconds 5
```

The results for all three pages:

```text
http://127.0.0.1:8770/api/products  (1 user, 5 s)
  requests   369  (74 per second)
  answers    200: 369
  errors     0  (0.0%)
  time (ms)  p50 14   p95 15   p99 16   max 17
http://127.0.0.1:8770/api/search?q=book  (1 user, 5 s)
  requests   90  (18 per second)
  answers    200: 90
  errors     0  (0.0%)
  time (ms)  p50 56   p95 58   p99 60   max 60
http://127.0.0.1:8770/api/report  (1 user, 5 s)
  requests   25  (5 per second)
  answers    200: 25
  errors     0  (0.0%)
  time (ms)  p50 206   p95 208   p99 209   max 210
```

All fine for one user. Every page is well under its target.

## Step 5: Measure many users at once

Now the agreed number of users, with the targets. `--max-p95` and `--max-errors` make the script say clearly when a target is broken:

```bash
python speed_check.py "http://127.0.0.1:8770/api/search?q=book" --users 10 --seconds 10 --max-p95 300 --max-errors 1
```

(Put addresses with `?` in quotes, or zsh on macOS complains.)

```text
http://127.0.0.1:8770/api/products  (10 users, 10 s)
  requests   7530  (752 per second)
  answers    200: 7530
  errors     0  (0.0%)
  time (ms)  p50 13   p95 15   p99 17   max 21
http://127.0.0.1:8770/api/search?q=book  (10 users, 10 s)
  requests   196  (19 per second)
  answers    200: 196
  errors     0  (0.0%)
  time (ms)  p50 536   p95 542   p99 543   max 544
  TOO SLOW OR FAILING: p95 542 ms is above 300 ms
http://127.0.0.1:8770/api/report  (10 users, 10 s)
  requests   42961  (4251 per second)
  answers    200: 200, 503: 42761
  errors     42761  (99.5%)
  time (ms)  p50 1   p95 2   p99 3   max 208
  TOO SLOW OR FAILING: errors 99.5% are above 1.0%
```

## Step 6: Read the numbers

Compare each page with its one-user baseline:

| Page | 1 user | 10 users | What it means |
| --- | --- | --- | --- |
| Products | p95 15 ms, 74/s | p95 15 ms, **752/s** | **Healthy.** Ten times the users, ten times the work, same speed |
| Search | p95 58 ms, 18/s | p95 **542 ms**, still **19/s** | **Doesn't scale.** More users, but no more work done: requests wait in a queue, one at a time. Each user waits for the nine before them |
| Report | 0 errors | **99.5% errors** (503 "Too busy") | **Breaks under load.** It can only serve a few people at once. Everyone else gets an error |

Three lessons you'll use at every job:

- **Always read errors before speed.** The report's p95 of **2 ms** looks great. It's fast because it's failing: an error answer takes no work. A fast failure is still a failure.
- **Requests per second tells you if it scales.** If more users don't give more requests per second, something is serialized: a lock, a single database connection, one worker.
- **Compare with the baseline.** "542 ms" alone means little. "58 ms for one user, 542 ms for ten" points straight at the problem.

**Report it with numbers:** "Search: p95 58 ms for 1 user, 542 ms for 10 users; requests per second stays at 19. Looks like requests are handled one at a time." Developers can work with that.

To see what "fixed" looks like, stop the practice API (**Ctrl+C**), start `python practice_api.py --fixed`, and check again:

```text
http://127.0.0.1:8770/api/search?q=book  (10 users, 10 s)
  requests   1802  (179 per second)
  answers    200: 1802
  errors     0  (0.0%)
  time (ms)  p50 56   p95 59   p99 61   max 63
http://127.0.0.1:8770/api/report  (10 users, 10 s)
  requests   490  (48 per second)
  answers    200: 490
  errors     0  (0.0%)
  time (ms)  p50 206   p95 210   p99 212   max 213
```

Same speed as one user, ten times the work. That's what a healthy page looks like.

## Step 7: Turn the targets into tests

Once the team agrees on targets, put them in `tests/test_speed.py`. Then anyone can run the whole check with one command, before every release:

```python
--8<-- "modules/work_playbooks/check_api_speed/templates/speed_check/tests/test_speed.py"
```

Change `BASE_URL` and the `TARGETS` table to your pages. Then run it, with the practice API running **with** its problems:

```bash
python -m pytest
```

```text
E       AssertionError: p95 is 575 ms, target 300 ms
E       AssertionError: 99.5% errors: {503: 20077, 200: 100}
...
FAILED tests/test_speed.py::test_page_is_fast_enough[/api/search?q=book-10-300-1]
FAILED tests/test_speed.py::test_page_is_fast_enough[/api/report-10-1000-1]
========================= 2 failed, 1 passed in 15.78s =========================
```

Under each failure, pytest also prints the full numbers (the `Captured stdout` part), ready for the bug report. On the fixed API: `3 passed in 15.30s`.

Each check runs 5 seconds. For a longer run: `SPEED_SECONDS=30 python -m pytest` (Windows: set `$env:SPEED_SECONDS="30"` first).

### Use it on your own app

1. Get the targets and the OK (step 2). Fill in `test_plan.md`.
2. Measure one user per page, then the agreed users. Start small: 5 users, then 10.
3. Pages that need a login: add the header, `-H "Authorization: Bearer $TOKEN"`. In `test_speed.py`, pass `headers=` to `run()`.
4. Put the agreed targets in `TARGETS`. Run before every release, and compare with the last run.
5. You don't need `practice_api.py`. It's only for practice.

## Step 8: Know the limits of this check

This check answers "are these pages fast enough for N users right now?". It is not a full load test. Know when you need more:

| Question | What to use |
| --- | --- |
| Where does it break? How many users can it take? | A load testing tool: [Locust](https://locust.io/) (Python) or [k6](https://k6.io/), raising users step by step |
| Does it stay fast for hours? Memory leaks? | A long run (soak test) with the same tools, while someone watches the servers |
| Is the page fast in the browser? | Browser tools such as Lighthouse: images, scripts, page size |
| Why is it slow? | The developers' tools: logs, database query times, monitoring |

Your numbers are also only as good as your setup. Run from a computer near the servers, on a quiet network. And run each check twice: if the numbers differ a lot, find out why before you report anything.

## Step 9: When it goes wrong

| You see | What it means | Fix |
| --- | --- | --- |
| `answers    failed: 6466` and `errors     6466  (100.0%)` | Nothing is running at that address, or the address is wrong | Start the practice API. For your app, check the URL in a browser or with curl |
| `no matches found: http://127.0.0.1:8770/api/search?q=book` | zsh treats `?` as a pattern | Put the address in quotes |
| `OSError: [Errno 48] Address already in use` (starting the practice API) | It's already running in another terminal | Use the one that's running, or stop it with **Ctrl+C** |
| p95 is fine, but errors are high | The page is failing fast | Read the `answers` line: 429 means you were rate limited, 503 too busy, 500 a crash. Report the errors first |
| Every answer is `401` | The page needs a login | Add `-H "Authorization: Bearer $TOKEN"` |
| Numbers jump between runs | Your network, your computer, or other people on the test environment | Run again, run from closer to the servers, and say in the report how much it varied |
| `429 Too Many Requests` | The system has a rate limit. That's protection working, not a speed result | Ask for the limit to be raised for your test, or test with fewer users |

When you're done: **Ctrl+C** in the first terminal stops the practice API.

Still stuck? Go deeper:

- [Performance testing topic](../../advanced-testing/performance-testing/index.md): load, stress and soak tests with real tools
- [Automate API tests, step by step](../automate-api-tests/index.md): check the answers are right before you check they're fast

## Templates

**Every file is below, ready to copy.** The whole folder is also [on GitHub](https://github.com/arshaduzzaman-sm/myopensdet/tree/main/modules/work_playbooks/check_api_speed/templates).

=== "test_plan.md"

    ```markdown
    --8<-- "modules/work_playbooks/check_api_speed/templates/speed_check/test_plan.md"
    ```

=== "practice_api.py"

    ```python
    --8<-- "modules/work_playbooks/check_api_speed/templates/speed_check/practice_api.py"
    ```

## References

- [Google SRE book: Service level objectives](https://sre.google/sre-book/service-level-objectives/) (why percentiles, not averages)
- [Python: statistics.quantiles](https://docs.python.org/3/library/statistics.html#statistics.quantiles)
- [Locust documentation](https://docs.locust.io/en/stable/)
- [k6 documentation](https://grafana.com/docs/k6/latest/)

Written for Python 3.13, pytest 9 and requests 2.34. Outputs captured November 2026. Links checked: November 2026.
