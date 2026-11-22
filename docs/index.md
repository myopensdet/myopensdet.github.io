---
title: "myOpenSDET: Learn Software Testing and Test Automation, Step by Step"
description: "Free, step-by-step SDET course with Python. Learn API, database, UI, BDD and performance testing with real templates you can copy."
hide:
  - navigation
  - toc
  - footer
  - author
  - feedback
  - path
updated: "2026-11-22"
---

<div class="zts-hero" markdown>

<div markdown>

# myOpenSDET

<p class="zts-hero__lead">Everything you need to test software well, in one place.</p>

<p class="zts-hero__sub">Learn software testing and test automation, step by step. Real templates and code you can use at work. Free.</p>

[Start learning](start-here/index.md){ .md-button .md-button--primary }
[Why I made this](#why-i-made-this){ .md-button }

</div>

<div class="zts-term" role="img" aria-label="A terminal running pytest: six tests about logging in, the cart, checkout, the API, the database and the web page all pass.">
<div class="zts-term__bar" aria-hidden="true"><span class="zts-term__dot"></span><span class="zts-term__dot"></span><span class="zts-term__dot"></span><span class="zts-term__title">practice-app-tests</span></div>
<div class="zts-term__body" aria-hidden="true">
<span class="zts-term__line" style="--i:0"><span class="zts-term__prompt">$ </span>pytest -v</span>
<span class="zts-term__line zts-term__dim" style="--i:1">collected 6 items</span>
<span class="zts-term__line" style="--i:2">test_login.py::test_arshad_can_log_in <span class="zts-term__pass">PASSED</span><span class="zts-term__dim zts-term__pct">  [ 16%]</span></span>
<span class="zts-term__line" style="--i:3">test_cart.py::test_add_two_books <span class="zts-term__pass">PASSED</span><span class="zts-term__dim zts-term__pct">  [ 33%]</span></span>
<span class="zts-term__line" style="--i:4">test_checkout.py::test_order_is_created <span class="zts-term__pass">PASSED</span><span class="zts-term__dim zts-term__pct">  [ 50%]</span></span>
<span class="zts-term__line" style="--i:5">test_api.py::test_products_return_200 <span class="zts-term__pass">PASSED</span><span class="zts-term__dim zts-term__pct">  [ 66%]</span></span>
<span class="zts-term__line" style="--i:6">test_db.py::test_order_is_saved <span class="zts-term__pass">PASSED</span><span class="zts-term__dim zts-term__pct">  [ 83%]</span></span>
<span class="zts-term__line" style="--i:7">test_ui.py::test_checkout_button_works <span class="zts-term__pass">PASSED</span><span class="zts-term__dim zts-term__pct">  [100%]</span></span>
<span class="zts-term__line zts-term__summary" style="--i:8">6 passed in 1.42s</span>
<span class="zts-term__line" style="--i:9"><span class="zts-term__prompt">$ </span><span class="zts-term__cursor"></span></span>
</div>
</div>

</div>

## What is an SDET?

An **SDET** (Software Development Engineer in Test) is a tester who writes code to test software.
Instead of clicking through an app by hand every day, an SDET writes small programs that do the checking, again and again, in seconds. The window above shows exactly that: six checks on an online shop, all done in about one second.

You don't need any coding experience to start here. Every lesson explains one idea at a time, shows you exactly what to type, and shows you what you should see.

## I need to…

Got a task at work today? Pick it and go straight to the page that helps. The [Work Playbooks](work-playbooks/index.md) walk one real task from start to report.

<div class="zts-tasks" markdown>

-   :lucide-list-checks: **[Test a new API endpoint by Friday](work-playbooks/new-api-endpoint/index.md)**

    Plan, probe, check and report, with scripts for your own app.

-   :lucide-file-json: **[Test a whole API from its Swagger file](work-playbooks/api-from-openapi/index.md)**

    Every endpoint listed, the spec reviewed, checks for the pipeline.

-   :lucide-plug-zap: **[Automate API tests, step by step](work-playbooks/automate-api-tests/index.md)**

    Install, read the spec, plan, copy GET, POST, PUT and DELETE tests, run.

-   :lucide-key-round: **[Test login and permissions, step by step](work-playbooks/test-login-and-permissions/index.md)**

    Tokens, logout, and "can user A see user B's data?", with ready tests.

-   :lucide-database: **[Check data in a database, step by step](work-playbooks/check-database-data/index.md)**

    Safe access, a plan, and ready checks for duplicates, orphans and wrong totals.

-   :lucide-file-up: **[Test file upload and CSV import, step by step](work-playbooks/test-file-upload-and-import/index.md)**

    Size limits, renamed files, Excel CSVs and half-saved imports.

-   :lucide-layers: **[Test several databases](core-automation/multi-database-testing/index.md)**

    One test on MySQL, PostgreSQL, SQLite and MongoDB.

-   :lucide-message-square-text: **[Set up BDD](core-automation/bdd-testing/index.md)**

    Tests in plain English with behave or pytest-bdd.

-   :lucide-mouse-pointer-click: **[Automate UI tests, step by step](work-playbooks/automate-ui-tests/index.md)**

    Install Playwright, pick the flows, copy login, cart and checkout tests, run.

-   :lucide-container: **[Run tests in Docker](infrastructure/docker-for-testers/index.md)**

    The same tests, the same way, on any computer.

-   :lucide-shuffle: **[Fix a flaky test](advanced-testing/flaky-tests-and-speed/index.md)**

    For tests that pass one day and fail the next.

-   :lucide-bug: **[Write a bug report](think-like-a-tester/bug-reports/index.md)**

    Report a bug so a developer can fix it fast.

-   :lucide-clipboard-list: **[Plan testing for a feature](think-like-a-tester/test-strategy-and-planning/index.md)**

    Decide what to test first, on one page.

-   :lucide-gauge: **[Check API speed, step by step](work-playbooks/check-api-speed/index.md)**

    Agree targets, measure one user then many, read p95 and errors.

-   :lucide-code: **[Learn Python for testing](start-here/python-for-testers/index.md)**

    Just enough Python to write real tests.

-   :lucide-briefcase: **[Prepare for an interview](professional-sdet/interview-preparation/index.md)**

    Common questions, coding tasks and clear answers.

</div>

## Pick your path

Not sure where to begin? Choose the one that sounds most like you. Each path lists lessons in the right order.

<div class="grid cards zts-paths" markdown>

-   :lucide-footprints:{ .lg .middle } **Manual tester to automation**

    ---

    You test by hand today and want to automate. Start with Python, then pytest, then your first API test.

    [See the manual tester path](learning-path.md#manual-tester-to-automation)

-   :lucide-trending-up:{ .lg .middle } **Build a whole test suite**

    ---

    You can write tests. Now build whole frameworks, run them in CI, and test databases and BDD.

    [See the test suite path](learning-path.md#build-a-whole-test-suite)

-   :lucide-mountain:{ .lg .middle } **Design how a team tests**

    ---

    Design test systems, test at scale, and lead quality for a team.

    [See the team path](learning-path.md#design-how-a-team-tests)

-   :lucide-calendar-check:{ .lg .middle } **Interview prep in 4 weeks**

    ---

    A week-by-week plan to get ready for SDET interviews.

    [See the 4-week plan](learning-path.md#interview-prep-in-4-weeks)

</div>

Not sure what you already know? Open the [Skills Matrix](start-here/skills-matrix.md), tick what you can do, and the first empty box is your next lesson.

## The route

The site follows six stages. Go in order, or jump to the one you need today.

<div class="zts-route" markdown>

1.  **[Start Here](start-here/index.md)**

    Set up your computer and learn just enough Python for testing.

2.  **[Think Like a Tester](think-like-a-tester/index.md)**

    What to test and why: test design, test cases, bug reports, plans.

3.  **[Core Automation](core-automation/index.md)**

    pytest, API, database, BDD and Playwright tests, with templates.

4.  **[Infrastructure](infrastructure/index.md)**

    CI/CD, Docker, Linux, networking and debugging.

5.  **[Advanced Testing](advanced-testing/index.md)**

    Performance, security, contracts, microservices, mobile and AI.

6.  **[The Professional SDET](professional-sdet/index.md)**

    Teamwork, releases, interviews, and leading quality.

</div>

Need a quick answer instead? The [Toolbox](toolbox/index.md) has cheat sheets, ready lists of test ideas, and every template in one place.

## How every lesson works

Every lesson follows the same pattern, so you always know what comes next.

1. **In plain words.** The idea, explained with an everyday example.
2. **Step by step.** Exactly what to type, and what you should see after each step.
3. **The template.** Code you can copy that really runs, with its tests.
4. **Common mistakes.** The errors people hit, and how to fix them.
5. **Try it yourself.** A small exercise, with the answer hidden until you want it.

The examples come from real work: the tasks, plans, code and checklists people use in testing jobs every day. Every guide is written so you can use it on your own app.

## Why I made this

As a tester, I kept meeting the same problem. The answers I needed were all online: in official guides, blog posts, conference talks, open-source projects and forum answers. But they were spread across a hundred tabs, written for different levels, and almost never in the order a working tester needs them.

So I did what testers do. I collected the evidence, checked it, and put it in order. This site is the result.

Nothing here is a secret, and I don't claim to have invented it. What I added is the work around it:

- **One place, one order.** From your first test to leading quality for a whole team.
- **Checked, not copied.** I ran every command myself. Every output on a page comes from a real run.
- **Ready for real work.** Plans, scripts and checklists you can use on your own app tomorrow.
- **Credit where it's due.** Every page links to its original sources, so you can go deeper.

I believe good testing knowledge should be free and easy to find. If one person gets unstuck at work, passes an interview, or moves from manual testing into automation because of a page here, it was worth building.

Thank you to everyone who shares what they know. This site stands on your work.

**Arshaduzzaman SM**
