---
title: "Software Testing Glossary: Every SDET Term in Plain English"
description: "Plain-English meanings of every testing and automation term used on myOpenSDET, each linked to the lesson that teaches it."
tags:
  - Quick reference
updated: "2026-11-22"
nav_title: "Glossary"
order: 40
nav_section: "toolbox"
summary: "Every testing word on this site, in plain English."
---

# Glossary

Every testing word on this site, in plain English. Each one links to the lesson
that teaches it.

!!! tip "Two quick ways to use it"
    - **Hover** over a short form like API or BDD on any page to see what it means.
    - **Search** with the box at the top: type a word and it shows the meaning here.

<!-- BEGIN glossary (generated from data/glossary.yml, do not edit by hand) -->

<nav class="zts-az" aria-label="Jump to a letter" markdown>[A](#a) [B](#b) [C](#c) [D](#d) [E](#e) [F](#f) [G](#g) [H](#h) [I](#i) [J](#j) [K](#k) [L](#l) [M](#m) [N](#n) [O](#o) [P](#p) [Q](#q) [R](#r) [S](#s) [T](#t) [U](#u) [V](#v) [W](#w) [X](#x)</nav>

## A

[](){ #acceptance-criteria }**Acceptance criteria**
:   The list of things a feature must do before the team calls it finished. Testers turn each one into tests.

    Learn more: [Test cases](think-like-a-tester/test-cases/index.md)

[](){ #accessibility }**Accessibility**
:   How easy the app is to use for everyone, including people who use a screen reader, a keyboard only, or large text.

    Learn more: [Accessibility testing](advanced-testing/accessibility-testing/index.md)

[](){ #ajax }**AJAX (Asynchronous JavaScript and XML)**
:   When JavaScript in a web page asks the server for data in the background and updates the page without loading a new one. Today the data is almost always JSON.

    Learn more: [How the web works](core-automation/api-testing/how-the-web-works.md)

[](){ #ambiguity }**Ambiguity**
:   Words that two people can read in different ways, like "fast" or "recent". Testers ask for a number or a clear rule instead.

    Learn more: [Finding ambiguity and missing cases](think-like-a-tester/static-testing-and-reviews/finding-ambiguity-and-missing-cases.md)

[](){ #api }**API (Application Programming Interface)**
:   A way for one program to ask another program for data or to do something. Like a waiter who takes your order to the kitchen and brings back your food.

    Learn more: [API testing](core-automation/api-testing/index.md)

[](){ #api-client }**API client**
:   A small class in a test project that holds the base address, headers, timeout and logging for one API, so tests do not repeat them.

    Learn more: [An API client class](core-automation/api-testing/api-client-class.md)

[](){ #api-key }**API key**
:   A secret code an app sends with every request, usually in a header, so the API knows who is calling.

    Learn more: [Authentication](core-automation/api-testing/authentication.md)

[](){ #api-test }**API test**
:   A test that sends a real request to the app's API and checks the status code and the data that come back.

    Learn more: [The test levels](think-like-a-tester/test-levels-and-the-pyramid/the-test-levels.md)

[](){ #assertion }**Assertion**
:   The line in a test that checks the result. If the check is false, the test fails.

    Learn more: [Tests and asserts](core-automation/pytest-framework/tests-and-asserts.md)

[](){ #atdd }**ATDD (Acceptance Test-Driven Development)**
:   The team writes the acceptance tests for a feature before it is built, then builds until they pass.

    Learn more: [What is BDD](core-automation/bdd-testing/what-is-bdd.md)

[](){ #auto-waiting }**Auto-waiting**
:   Playwright waits by itself until an element can be used before it clicks or types, so tests don't need fixed waits.

    Learn more: [Waits](core-automation/ui-automation/waits.md)

[](){ #automation }**Automation**
:   Letting a program do a check that a person would otherwise do by hand, so it can run again and again in seconds.

    Learn more: [The SDET role](think-like-a-tester/the-sdet-role/index.md)

[](){ #automation-roi }**Automation ROI**
:   ROI means return on investment. It is whether an automated test saves more time than it costs to build and keep working, and how soon.

    Learn more: [What not to automate](think-like-a-tester/test-strategy-and-planning/what-not-to-automate.md)

## B

[](){ #backend }**Backend**
:   The part of an app that runs on the servers: the API, the rules, and the database.

    Learn more: [How the web works](core-automation/api-testing/how-the-web-works.md)

[](){ #background-job }**Background job**
:   Work an app does after it has already answered the request, like sending an email or writing a history row.

    Learn more: [Waiting for late writes](core-automation/api-and-database/waiting-for-async-writes.md)

[](){ #bdd }**BDD (Behavior-Driven Development)**
:   A way of writing tests as plain English examples, like "Given I am logged in, When I add a book, Then my cart has 1 item".

    Learn more: [What is BDD](core-automation/bdd-testing/what-is-bdd.md)

[](){ #bearer-token }**Bearer token**
:   A secret you get from logging in and send in the Authorization header on every request. Whoever holds it gets in, until it expires.

    Learn more: [Authentication](core-automation/api-testing/authentication.md)

[](){ #boundary-value }**Boundary value**
:   A value right at the edge of what is allowed, like 0, 1, 99 and 100 for "1 to 99". Bugs love edges.

    Learn more: [Boundary values](think-like-a-tester/test-design-techniques/boundary-values.md)

[](){ #branch-coverage }**Branch coverage**
:   The share of ways through each if (yes and no) that the tests took. It finds paths that line coverage misses.

    Learn more: [Statement and branch coverage](think-like-a-tester/test-design-techniques/statement-and-branch-coverage.md)

[](){ #browser-context }**Browser context**
:   A fresh, private browser profile with its own cookies and tabs. UI tests get a new one each, so nothing leaks between tests.

    Learn more: [How browsers and locators work](core-automation/ui-automation/how-browsers-and-locators-work.md)

[](){ #bug-lifecycle }**Bug lifecycle**
:   The states a bug moves through, like new, triaged, in progress, fixed, verified and closed.

    Learn more: [The bug lifecycle](think-like-a-tester/bug-reports/bug-lifecycle.md)

[](){ #bug-report }**Bug report**
:   A short note that tells a developer what went wrong, how to make it happen again, and what should have happened instead.

    Learn more: [Bug reports](think-like-a-tester/bug-reports/index.md)

## C

[](){ #checklist-based-testing }**Checklist-based testing**
:   Testing with a short list of things that must be true for every feature of one kind, like every web form.

    Learn more: [Checklist-based testing](think-like-a-tester/test-design-techniques/checklist-based-testing.md)

[](){ #checksum }**Checksum**
:   A short fingerprint made from data. The same data always gives the same fingerprint, so two fingerprints that differ mean the data differs.

    Learn more: [Cross-database comparison](core-automation/multi-database-testing/cross-database-comparison.md)

[](){ #cicd }**CI/CD (Continuous Integration and Continuous Delivery)**
:   A setup that builds the app and runs the tests every time someone changes the code, then helps ship it.

    Learn more: [CI/CD for testers](infrastructure/ci-cd/index.md)

[](){ #class }**Class**
:   A blueprint that bundles data and actions together. Page objects and API clients are classes.

    Learn more: [Classes and objects](start-here/python-for-testers/classes-and-objects.md)

[](){ #client }**Client**
:   The program that asks: a browser, a phone app, or your test. It sends a request and waits for the answer.

    Learn more: [How the web works](core-automation/api-testing/how-the-web-works.md)

[](){ #conftestpy }**conftest.py**
:   A file pytest loads by itself, where you put fixtures and options that many test files share.

    Learn more: [Fixtures and conftest.py](core-automation/pytest-framework/fixtures-and-conftest.md)

[](){ #constraint }**Constraint**
:   A rule written into a database table, such as NOT NULL or UNIQUE. The database refuses any row that breaks it.

    Learn more: [Integrity: keys and rules](core-automation/database-testing/integrity-constraints.md)

[](){ #container }**Container**
:   A small, sealed box that holds an app and everything it needs, so it runs the same way on every computer.

    Learn more: [Docker for testers](infrastructure/docker-for-testers/index.md)

[](){ #contract-testing }**Contract testing**
:   Checking that two services still agree on the shape of the messages they send each other.

    Learn more: [Contract testing](advanced-testing/contract-testing/index.md)

[](){ #cross-browser-testing }**Cross-browser testing**
:   Running the same tests on several browsers, like Chrome, Firefox and Safari, to find bugs that show in only one.

    Learn more: [Cross-browser runs](core-automation/ui-automation/cross-browser-runs.md)

[](){ #crud }**CRUD (Create, Read, Update, Delete)**
:   The four things an app does with stored data. In SQL they are INSERT, SELECT, UPDATE and DELETE.

    Learn more: [CRUD tests](core-automation/database-testing/crud-tests.md)

## D

[](){ #data-migration }**Data migration**
:   Moving data from one database to another, often once, such as from MySQL to PostgreSQL.

    Learn more: [Migration and ETL validation](core-automation/multi-database-testing/migration-and-etl-validation.md)

[](){ #data-driven-testing }**Data-driven testing**
:   Writing a check once and running it with many rows of data, often read from a file.

    Learn more: [One test, many rows](core-automation/data-driven-testing/one-test-many-rows.md)

[](){ #database }**Database**
:   An organized store of data that an app saves to and reads from, like a set of very large tables.

    Learn more: [Database testing](core-automation/database-testing/index.md)

[](){ #database-schema }**Database schema**
:   The shape of a database. Which tables it has, which columns each table has, and their types and rules.

    Learn more: [Schema tests](core-automation/database-testing/schema-tests.md)

[](){ #decision-table }**Decision table**
:   A table that lists every mix of conditions, like "member" and "order over $50", with the result for each. Each row becomes a test.

    Learn more: [Decision tables](think-like-a-tester/test-design-techniques/decision-tables.md)

[](){ #defect-clustering }**Defect clustering**
:   Most bugs hide in a few parts of a system. When you find one bug, look for more nearby.

    Learn more: [The seven testing principles](think-like-a-tester/the-sdet-role/seven-testing-principles.md)

[](){ #dictionary }**Dictionary**
:   In Python, a set of named values, like a product with a name and a price. API responses become dictionaries.

    Learn more: [Strings, lists and dictionaries](start-here/python-for-testers/strings-lists-and-dictionaries.md)

[](){ #docker }**Docker**
:   The most common tool for building and running containers.

    Learn more: [Docker for testers](infrastructure/docker-for-testers/index.md)

[](){ #docker-compose }**Docker Compose**
:   A Docker tool that starts several containers from one file, in the right order, so they can work together.

    Learn more: [Compose test environments](infrastructure/docker-for-testers/compose-test-environments.md)

[](){ #docker-image }**Docker image**
:   A read-only package with a program and everything it needs. Docker makes containers from it, like cakes from one recipe.

    Learn more: [Images and containers](infrastructure/docker-for-testers/images-and-containers.md)

[](){ #dockerfile }**Dockerfile**
:   A text file with the steps to build a Docker image, read from top to bottom.

    Learn more: [Dockerfile for a test suite](infrastructure/docker-for-testers/dockerfile-for-a-test-suite.md)

[](){ #dom }**DOM (Document Object Model)**
:   The page as the browser holds it right now, after JavaScript has changed it. It can differ from the HTML the server sent.

    Learn more: [How the web works](core-automation/api-testing/how-the-web-works.md)

[](){ #dynamic-testing }**Dynamic testing**
:   Testing by running the software and checking what it does.

    Learn more: [What static testing is](think-like-a-tester/static-testing-and-reviews/what-is-static-testing.md)

## E

[](){ #e2e }**E2E (End-to-end)**
:   A test that goes through the whole app the way a real user would, from the web page down to the database and back.

    Learn more: [Test levels and the pyramid](think-like-a-tester/test-levels-and-the-pyramid/index.md)

[](){ #edge-case }**Edge case**
:   A test right at a limit, like a code used at exactly 10 minutes. Bugs often hide at limits.

    Learn more: [The 9-step playbook](think-like-a-tester/learning-a-new-testing-area/the-9-step-playbook.md)

[](){ #endpoint }**Endpoint**
:   One address of an API that you can send a request to, like /products or /orders/42.

    Learn more: [API testing](core-automation/api-testing/index.md)

[](){ #entry-criteria }**Entry criteria**
:   What must be true before testing starts, like a reviewed story, a deployed build and ready test data.

    Learn more: [Entry and exit criteria](think-like-a-tester/test-strategy-and-planning/entry-and-exit-criteria.md)

[](){ #environment }**Environment**
:   One full copy of the app for a purpose, like your own computer, a shared test copy, or the live site.

    Learn more: [Environments](core-automation/pytest-framework/environments.md)

[](){ #equivalence-partitioning }**Equivalence partitioning**
:   Splitting inputs into groups that should behave the same, then testing one value from each group instead of all of them.

    Learn more: [Equivalence partitioning](think-like-a-tester/test-design-techniques/equivalence-partitioning.md)

[](){ #error-guessing }**Error guessing**
:   Trying the inputs and actions that often break software, like emoji, double clicks or 29 February.

    Learn more: [Error guessing](think-like-a-tester/test-design-techniques/error-guessing.md)

[](){ #etl }**ETL (Extract, Transform, Load)**
:   A job that copies data from one place to another and changes it on the way, often every night.

    Learn more: [Migration and ETL validation](core-automation/multi-database-testing/migration-and-etl-validation.md)

[](){ #example-mapping }**Example mapping**
:   A way to run a Three Amigos meeting with coloured cards for the story, its rules, examples and open questions.

    Learn more: [Writing scenarios with the business](core-automation/bdd-testing/writing-scenarios-with-the-business.md)

[](){ #exit-criteria }**Exit criteria**
:   What must be true before testing is done, like no failing tests and no open critical bugs. Agreed before testing starts.

    Learn more: [Entry and exit criteria](think-like-a-tester/test-strategy-and-planning/entry-and-exit-criteria.md)

[](){ #expected-result }**Expected result**
:   Exactly what should happen when you run a test, and what must not. The most important line of a test case.

    Learn more: [Anatomy of a test case](think-like-a-tester/test-cases/anatomy-of-a-test-case.md)

[](){ #exploratory-testing }**Exploratory testing**
:   Testing by learning the app as you go, trying ideas and following anything that looks odd, instead of following a script.

    Learn more: [Exploratory testing](think-like-a-tester/test-design-techniques/exploratory-testing.md)

## F

[](){ #feature-file }**Feature file**
:   A file ending in .feature that holds one feature and its scenarios, written in Gherkin.

    Learn more: [Gherkin and feature files](core-automation/bdd-testing/gherkin-and-feature-files.md)

[](){ #fixture }**Fixture**
:   In pytest, a small helper that gets something ready for a test, like a logged-in user, and cleans it up afterwards.

    Learn more: [Fixtures and conftest.py](core-automation/pytest-framework/fixtures-and-conftest.md)

[](){ #flaky-test }**Flaky test**
:   A test that sometimes passes and sometimes fails without any change to the code.

    Learn more: [Flaky tests and speed](advanced-testing/flaky-tests-and-speed/index.md)

[](){ #foreign-key }**Foreign key**
:   A column whose value must exist in another table, such as an order's customer id. It keeps links between tables real.

    Learn more: [Integrity: keys and rules](core-automation/database-testing/integrity-constraints.md)

[](){ #framework }**Framework**
:   The shared structure of a test project, such as folders, settings and helpers, so every test is written the same way.

    Learn more: [pytest framework](core-automation/pytest-framework/index.md)

[](){ #frontend }**Frontend**
:   The part of an app that runs on the user's device: the web page, its JavaScript, or the phone app.

    Learn more: [How the web works](core-automation/api-testing/how-the-web-works.md)

[](){ #function }**Function**
:   A named piece of work that takes inputs and returns a result. Every pytest test is a function.

    Learn more: [Functions](start-here/python-for-testers/functions.md)

## G

[](){ #gherkin }**Gherkin**
:   The plain-English format BDD tests are written in, using the words Given, When and Then.

    Learn more: [Gherkin and feature files](core-automation/bdd-testing/gherkin-and-feature-files.md)

[](){ #git }**Git**
:   A tool that saves every change to your code, so you can go back in time and work with others safely.

    Learn more: [Git in a team](professional-sdet/git-in-a-team/index.md)

## H

[](){ #happy-path }**Happy path**
:   The normal way a user uses a feature, with good data and no mistakes. It is usually the first thing you test.

    Learn more: [The 9-step playbook](think-like-a-tester/learning-a-new-testing-area/the-9-step-playbook.md)

[](){ #headless-browser }**Headless browser**
:   A browser running without a window. Faster, and what test pipelines use.

    Learn more: [How browsers and locators work](core-automation/ui-automation/how-browsers-and-locators-work.md)

[](){ #health-check }**Health check**
:   A small command that tells whether a service is ready to use, so other services can wait for it.

    Learn more: [Compose test environments](infrastructure/docker-for-testers/compose-test-environments.md)

[](){ #html }**HTML (HyperText Markup Language)**
:   The text a web page is made of, with tags like <h1> for a heading and <button> for a button. The browser turns it into what you see.

    Learn more: [How the web works](core-automation/api-testing/how-the-web-works.md)

[](){ #http }**HTTP (Hypertext Transfer Protocol)**
:   The set of rules web browsers and APIs use to send requests and answers.

    Learn more: [Networking for testers](infrastructure/networking-for-testers/index.md)

[](){ #http-method }**HTTP method**
:   The word at the start of a request that says what to do, like GET to read, POST to create, PUT or PATCH to change and DELETE to remove.

    Learn more: [GET, POST, PUT, PATCH, DELETE](core-automation/api-testing/http-methods.md)

## I

[](){ #ice-cream-cone }**Ice cream cone**
:   A test suite shaped like an upside-down pyramid, with many slow UI tests and very few unit tests. It is slow and often flaky.

    Learn more: [The test pyramid](think-like-a-tester/test-levels-and-the-pyramid/the-test-pyramid.md)

[](){ #idempotent }**Idempotent**
:   A request is idempotent when sending it twice gives the same result as sending it once. PUT and DELETE are, POST is not.

    Learn more: [GET, POST, PUT, PATCH, DELETE](core-automation/api-testing/http-methods.md)

[](){ #iframe }**Iframe**
:   A web page shown inside another web page, like a payment form from a payment company. Tests must reach into it to use it.

    Learn more: [Forms, dialogs, frames and tabs](core-automation/ui-automation/forms-dialogs-frames-and-tabs.md)

[](){ #image-digest }**Image digest**
:   A long code starting with sha256 that names one exact Docker image. Unlike a tag, it can never point to a different image.

    Learn more: [Images and containers](infrastructure/docker-for-testers/images-and-containers.md)

[](){ #inspection }**Inspection**
:   The most formal kind of review, with set roles, a checklist, prepared reviewers and a written list of findings.

    Learn more: [Review types](think-like-a-tester/static-testing-and-reviews/review-types.md)

[](){ #integration-test }**Integration test**
:   A test that checks two or more parts of the app work together, like the API and the database.

    Learn more: [Test levels and the pyramid](think-like-a-tester/test-levels-and-the-pyramid/index.md)

[](){ #istqb }**ISTQB (International Software Testing Qualifications Board)**
:   A group that writes testing exams and a shared list of testing words, used in many countries.

    Learn more: [The seven testing principles](think-like-a-tester/the-sdet-role/seven-testing-principles.md)

## J

[](){ #join }**JOIN**
:   SQL that reads two tables together by matching a column, such as each order with its customer.

    Learn more: [JOIN, GROUP BY and subqueries](core-automation/database-testing/joins-and-group-by.md)

[](){ #json }**JSON (JavaScript Object Notation)**
:   A simple text format for data, made of names and values in curly brackets. Most APIs send and receive JSON.

    Learn more: [JSON](start-here/python-for-testers/json.md)

[](){ #json-schema }**JSON Schema**
:   A file that describes the shape JSON must have, like which fields are required and what type each one is. Tests use it to check responses.

    Learn more: [Schema validation](core-automation/api-testing/schema-validation.md)

[](){ #junit-xml }**JUnit XML**
:   A test results file format that almost every CI tool can read, with one entry per test and its failure message.

    Learn more: [JUnit XML for pipelines](core-automation/reporting-and-logging/junit-xml-for-pipelines.md)

## K

[](){ #keyword-driven-testing }**Keyword-driven testing**
:   Writing tests as plain steps called keywords, like "Apply coupon". The code behind each keyword is written once.

    Learn more: [Keyword-driven: Robot Framework](core-automation/data-driven-testing/keyword-driven-robot-framework.md)

## L

[](){ #linter }**Linter**
:   A tool that reads code and points at bugs and risky patterns, like an unused import or an assert that can never fail.

    Learn more: [Static analysis tools](think-like-a-tester/static-testing-and-reviews/static-analysis-tools.md)

[](){ #load-testing }**Load testing**
:   Checking how the app behaves when many people use it at the same time.

    Learn more: [Performance testing](advanced-testing/performance-testing/index.md)

[](){ #locator }**Locator**
:   The instruction that tells a UI test which button, box or link on the page to use.

    Learn more: [Choosing locators](core-automation/ui-automation/choosing-locators.md)

[](){ #log-level }**Log level**
:   How important a log line is, from DEBUG (details) through INFO, WARNING and ERROR to CRITICAL. You choose which levels to keep.

    Learn more: [Logging in tests](core-automation/reporting-and-logging/logging-in-tests.md)

## M

[](){ #manual-testing }**Manual testing**
:   Testing by using the app yourself, by hand, and checking what happens.

    Learn more: [The SDET role](think-like-a-tester/the-sdet-role/index.md)

[](){ #marker }**Marker**
:   A label on a pytest test, like unit or ui, so you can run only the tests with that label.

    Learn more: [Markers](core-automation/pytest-framework/markers.md)

[](){ #microservice }**Microservice**
:   One small service that does one job. A big app can be made of many microservices talking to each other.

    Learn more: [Testing microservices](advanced-testing/testing-microservices/index.md)

[](){ #mock }**Mock**
:   A fake version of a real service, used in a test so you control exactly what it answers.

    Learn more: [Mocking and stubbing](advanced-testing/mocking-and-stubbing/index.md)

[](){ #multipart-form-data }**Multipart form data**
:   The kind of request body used to upload files. It is split into parts, one for each file and form field.

    Learn more: [File upload](core-automation/api-testing/file-upload.md)

## N

[](){ #negative-test }**Negative test**
:   A test that sends bad input on purpose, like a wrong code or a short password, to check the app refuses it.

    Learn more: [The 9-step playbook](think-like-a-tester/learning-a-new-testing-area/the-9-step-playbook.md)

[](){ #non-functional-testing }**Non-functional testing**
:   Testing how well the app works, not what it does. For example, how fast it is, how easy it is to use, and whether it stays up.

    Learn more: [Non-functional testing](think-like-a-tester/test-levels-and-the-pyramid/non-functional-testing.md)

[](){ #null }**NULL**
:   The value a database uses for nothing at all. It is not zero and not empty text, and you find it with IS NULL.

    Learn more: [SQL for testers](core-automation/database-testing/sql-for-testers.md)

## O

[](){ #oauth2 }**OAuth2**
:   A standard way to get access tokens from a separate token server, instead of sending a password to every API.

    Learn more: [Authentication](core-automation/api-testing/authentication.md)

[](){ #off-by-one-bug }**Off-by-one bug**
:   A bug where a limit is out by one step, like refusing age 18 when 18 should be allowed. Often caused by mixing up < and <=.

    Learn more: [Boundary values](think-like-a-tester/test-design-techniques/boundary-values.md)

## P

[](){ #page-object }**Page Object**
:   A class that holds everything a UI test needs about one page, so tests stay short and a page change is fixed in one place.

    Learn more: [Page Object Model](core-automation/ui-automation/page-object-model.md)

[](){ #pairwise-testing }**Pairwise testing**
:   Picking a small set of tests where every pair of settings, like Safari with PayPal, appears together at least once.

    Learn more: [Pairwise testing](think-like-a-tester/test-design-techniques/pairwise-testing.md)

[](){ #parametrize }**Parametrize**
:   A pytest feature that runs the same test many times, once for each row of values you give it.

    Learn more: [Parametrize](core-automation/pytest-framework/parametrize.md)

[](){ #path-parameter }**Path parameter**
:   A value that is part of the web address itself, like the 42 in /booking/42, usually the id of one thing.

    Learn more: [Query and path parameters](core-automation/api-testing/query-and-path-params.md)

[](){ #percentile }**Percentile**
:   A way to describe speed. The 95th percentile is the time that 95 out of 100 requests were as fast as, or faster than.

    Learn more: [Non-functional testing](think-like-a-tester/test-levels-and-the-pyramid/non-functional-testing.md)

[](){ #performance-testing }**Performance testing**
:   Measuring how fast the app is and how much it can handle before it slows down or breaks.

    Learn more: [Performance testing](advanced-testing/performance-testing/index.md)

[](){ #pesticide-paradox }**Pesticide paradox**
:   Running the same tests again and again finds fewer new bugs over time. New tests and new data find new bugs.

    Learn more: [The seven testing principles](think-like-a-tester/the-sdet-role/seven-testing-principles.md)

[](){ #pip }**pip**
:   The tool that installs Python packages, like pytest, into your virtual environment.

    Learn more: [Virtual environments and pip](start-here/python-for-testers/virtual-environments-and-pip.md)

[](){ #playbook }**Playbook**
:   A list of steps a team follows every time for the same kind of job, so nobody has to invent the plan again.

    Learn more: [The 9-step playbook](think-like-a-tester/learning-a-new-testing-area/the-9-step-playbook.md)

[](){ #playwright }**Playwright**
:   A tool that controls a real web browser from code, so a test can click, type and check a page.

    Learn more: [UI automation](core-automation/ui-automation/index.md)

[](){ #polling }**Polling**
:   Asking the same question again and again, a short time apart, until the answer is there or time runs out.

    Learn more: [Waiting for late writes](core-automation/api-and-database/waiting-for-async-writes.md)

[](){ #positive-test }**Positive test**
:   A test that checks something works when it should, like a refund within 30 days going through.

    Learn more: [Positive and negative cases](think-like-a-tester/test-cases/positive-and-negative-cases.md)

[](){ #pre-commit }**pre-commit**
:   A tool that runs checks automatically every time you commit, and stops the commit if something is wrong.

    Learn more: [Static analysis tools](think-like-a-tester/static-testing-and-reviews/static-analysis-tools.md)

[](){ #precondition }**Precondition**
:   The state the system must be in before a test starts, like "a customer with one delivered item".

    Learn more: [Anatomy of a test case](think-like-a-tester/test-cases/anatomy-of-a-test-case.md)

[](){ #primary-key }**Primary key**
:   The column that gives every row its own id, never empty and never repeated.

    Learn more: [Integrity: keys and rules](core-automation/database-testing/integrity-constraints.md)

[](){ #priority }**Priority**
:   How soon the team will fix a bug. The team decides it in triage, and the reporter can suggest one.

    Learn more: [Severity and priority](think-like-a-tester/bug-reports/severity-and-priority.md)

[](){ #pull-request }**Pull request**
:   A request to add your code changes to the team's main code. Others review it first.

    Learn more: [Git in a team](professional-sdet/git-in-a-team/index.md)

[](){ #pytest }**pytest**
:   The most popular tool for writing and running tests in Python.

    Learn more: [pytest framework](core-automation/pytest-framework/index.md)

## Q

[](){ #qa }**QA (Quality Assurance)**
:   All the work a team does to make sure the product is good, including testing.

    Learn more: [The SDET role](think-like-a-tester/the-sdet-role/index.md)

[](){ #query-parameter }**Query parameter**
:   A value after the question mark in a web address, like page=2, used to filter, sort or page results.

    Learn more: [Query and path parameters](core-automation/api-testing/query-and-path-params.md)

## R

[](){ #race-condition }**Race condition**
:   A bug that depends on which of two things happens first. It can pass a hundred times and then fail.

    Learn more: [Cleanup after API tests](core-automation/api-and-database/cleanup-after-api-tests.md)

[](){ #random-seed }**Random seed**
:   The starting number for random values. The same seed gives the same values again, so a random test can be repeated.

    Learn more: [Fake data with Faker](core-automation/data-driven-testing/fake-data-with-faker.md)

[](){ #redaction }**Redaction**
:   Hiding secrets like passwords and card numbers, for example by writing "***" instead, before they reach a log or report.

    Learn more: [Screenshots and request logs](core-automation/reporting-and-logging/screenshots-and-request-logs.md)

[](){ #regression-testing }**Regression testing**
:   Running tests again after a change, to make sure things that worked before still work.

    Learn more: [Regression, hotfixes and incidents](professional-sdet/regression-hotfixes-and-incidents/index.md)

[](){ #request-header }**Request header**
:   A short note sent with a request, like Accept or Authorization, that tells the server about the request.

    Learn more: [Headers and JSON](core-automation/api-testing/headers-and-json.md)

[](){ #rest }**REST (Representational State Transfer)**
:   The most common style of web API. You use web addresses for things and HTTP methods like GET and POST for actions.

    Learn more: [How the web works](core-automation/api-testing/how-the-web-works.md)

[](){ #risk }**Risk**
:   Something that could go wrong, and how much it would hurt users or the company. Testers test the biggest risks first.

    Learn more: [Learning a new testing area](think-like-a-tester/learning-a-new-testing-area/index.md)

[](){ #risk-based-testing }**Risk-based testing**
:   Spending most of your testing time where a bug is most likely and would hurt most, and testing those things first.

    Learn more: [Risk-based testing](think-like-a-tester/test-strategy-and-planning/risk-based-testing.md)

[](){ #rollback }**Rollback**
:   Undoing every change made in a transaction. Tests use it to leave the database exactly as they found it.

    Learn more: [Transactions and clean-up](core-automation/database-testing/transactions-and-cleanup.md)

## S

[](){ #savepoint }**Savepoint**
:   A point inside a transaction you can roll back to without undoing everything before it.

    Learn more: [Transactions and clean-up](core-automation/database-testing/transactions-and-cleanup.md)

[](){ #scenario-outline }**Scenario outline**
:   One Gherkin scenario with blanks, run once for each row of an Examples table.

    Learn more: [Scenario outlines](core-automation/bdd-testing/scenario-outlines.md)

[](){ #scope }**Scope**
:   What is part of a task, and what is not. Writing it down stops you from testing the wrong thing.

    Learn more: [Asking the right questions](think-like-a-tester/learning-a-new-testing-area/asking-the-right-questions.md)

[](){ #sdet }**SDET (Software Development Engineer in Test)**
:   A tester who writes code to test software.

    Learn more: [The SDET role](think-like-a-tester/the-sdet-role/index.md)

[](){ #seed-data }**Seed data**
:   Rows a test puts straight into the database before it starts, so the app has something to work with.

    Learn more: [Seed then call](core-automation/api-and-database/seed-then-call.md)

[](){ #server }**Server**
:   The program that answers requests. It runs the app's rules and talks to the database.

    Learn more: [How the web works](core-automation/api-testing/how-the-web-works.md)

[](){ #severity }**Severity**
:   How badly a bug hurts the people using the app, from critical (money, data or security) to trivial (a typo). The reporter sets it.

    Learn more: [Severity and priority](think-like-a-tester/bug-reports/severity-and-priority.md)

[](){ #smoke-test }**Smoke test**
:   A few quick tests that check the most important things work, before you spend time on deeper testing.

    Learn more: [Test levels and the pyramid](think-like-a-tester/test-levels-and-the-pyramid/index.md)

[](){ #source-of-truth }**Source of truth**
:   The one place everyone agrees holds the right data. Copies are checked against it.

    Learn more: [Why test several databases](core-automation/multi-database-testing/why-test-several-databases.md)

[](){ #sql }**SQL (Structured Query Language)**
:   The language used to ask a database for data or change it, like SELECT * FROM orders.

    Learn more: [SQL for testers](core-automation/database-testing/sql-for-testers.md)

[](){ #sql-injection }**SQL injection**
:   A security bug where text typed by a user changes the SQL the app runs. Passing values as parameters prevents it.

    Learn more: [Connecting from Python](core-automation/database-testing/connecting-from-python.md)

[](){ #state-transition }**State transition**
:   A move from one status to another, like an order going from paid to shipped. Testing them checks allowed moves work and the rest are refused.

    Learn more: [State transitions](think-like-a-tester/test-design-techniques/state-transitions.md)

[](){ #statement-coverage }**Statement coverage**
:   The share of code lines that ran at least once during the tests. 100% means every line ran, not that every line was checked.

    Learn more: [Statement and branch coverage](think-like-a-tester/test-design-techniques/statement-and-branch-coverage.md)

[](){ #static-analysis }**Static analysis**
:   Checking code for mistakes without running it, like a spell checker for code.

    Learn more: [Static analysis tools](think-like-a-tester/static-testing-and-reviews/static-analysis-tools.md)

[](){ #static-testing }**Static testing**
:   Checking work without running it, by reading stories, specs, plans and code, or by letting a tool read the code.

    Learn more: [What static testing is](think-like-a-tester/static-testing-and-reviews/what-is-static-testing.md)

[](){ #status-code }**Status code**
:   The number an API sends back to say how a request went, like 200 for OK or 404 for not found.

    Learn more: [Status codes](core-automation/api-testing/status-codes.md)

[](){ #step-definition }**Step definition**
:   The Python function that runs when a Gherkin step like "When I apply the coupon" matches its pattern.

    Learn more: [Step definitions](core-automation/bdd-testing/step-definitions.md)

[](){ #steps-to-reproduce }**Steps to reproduce**
:   The numbered actions in a bug report that make the bug happen again, written so someone else can follow them.

    Learn more: [What makes a great bug report](think-like-a-tester/bug-reports/what-makes-a-great-bug-report.md)

[](){ #stored-procedure }**Stored procedure**
:   Code saved inside the database and run by name, such as place_order. In PostgreSQL it is often written as a function.

    Learn more: [Stored procedures and triggers](core-automation/database-testing/procedures-and-triggers.md)

[](){ #stub }**Stub**
:   A very simple fake that always gives the same ready answer, so a test does not need the real thing.

    Learn more: [Mocking and stubbing](advanced-testing/mocking-and-stubbing/index.md)

## T

[](){ #table }**Table**
:   One set of rows and columns in a database, like one sheet in a spreadsheet. Each row is one thing, such as one order.

    Learn more: [SQL for testers](core-automation/database-testing/sql-for-testers.md)

[](){ #tdd }**TDD (Test-Driven Development)**
:   Writing a small failing test first, then the code that makes it pass, then tidying the code.

    Learn more: [What is BDD](core-automation/bdd-testing/what-is-bdd.md)

[](){ #test-case }**Test case**
:   One check written down step by step, with the expected result, so anyone can run it the same way.

    Learn more: [Anatomy of a test case](think-like-a-tester/test-cases/anatomy-of-a-test-case.md)

[](){ #test-charter }**Test charter**
:   One sentence that sets the goal of an exploratory testing session. Explore something, with some idea, to find out something.

    Learn more: [Exploratory testing](think-like-a-tester/test-design-techniques/exploratory-testing.md)

[](){ #test-condition }**Test condition**
:   One thing worth testing, found by reading the story. For example, "a code older than 10 minutes must not work".

    Learn more: [The test process and testware](think-like-a-tester/the-sdet-role/test-process-and-testware.md)

[](){ #test-data }**Test data**
:   The users, products, orders and other data a test needs to run.

    Learn more: [Data-driven testing](core-automation/data-driven-testing/index.md)

[](){ #test-data-factory }**Test data factory**
:   A small function that makes a complete, valid test object, so each test changes only what it is about.

    Learn more: [Test data factories](core-automation/data-driven-testing/test-data-factories.md)

[](){ #test-level }**Test level**
:   How much of the app a test uses at once, from one small function (unit) up to the whole system (end-to-end).

    Learn more: [The test levels](think-like-a-tester/test-levels-and-the-pyramid/the-test-levels.md)

[](){ #test-plan }**Test plan**
:   A short document that says what will be tested, how, by whom and when.

    Learn more: [Test plan](think-like-a-tester/test-strategy-and-planning/test-plan.md)

[](){ #test-pyramid }**Test pyramid**
:   A picture of a healthy test mix. Many small, fast unit tests at the bottom, fewer integration tests, and only a few slow end-to-end tests at the top.

    Learn more: [Test levels and the pyramid](think-like-a-tester/test-levels-and-the-pyramid/index.md)

[](){ #test-strategy }**Test strategy**
:   One page that says how a team tests every feature, at which levels, with which tools, and when a release is ready.

    Learn more: [Test strategy](think-like-a-tester/test-strategy-and-planning/test-strategy.md)

[](){ #testing-trophy }**Testing trophy**
:   Another picture of a healthy test mix, with static checks at the base and most tests checking parts working together.

    Learn more: [The testing trophy](think-like-a-tester/test-levels-and-the-pyramid/the-testing-trophy.md)

[](){ #testware }**Testware**
:   Everything testing produces, such as plans, test cases, test data, scripts, results and reports.

    Learn more: [The test process and testware](think-like-a-tester/the-sdet-role/test-process-and-testware.md)

[](){ #three-amigos }**Three Amigos**
:   A short meeting where a product owner, a developer and a tester agree on how a story should behave.

    Learn more: [Writing scenarios with the business](core-automation/bdd-testing/writing-scenarios-with-the-business.md)

[](){ #trace }**Trace**
:   A recording of a UI test run, with every action, a snapshot of the page before and after it, and the network calls. Opened in Playwright's trace viewer.

    Learn more: [Screenshots and traces](core-automation/ui-automation/screenshots-and-traces.md)

[](){ #traceability }**Traceability**
:   The link between each requirement and the tests that check it, so you can see what has no test.

    Learn more: [Traceability](think-like-a-tester/test-cases/traceability.md)

[](){ #traceability-matrix }**Traceability matrix**
:   A table with one row per requirement and the test cases that cover it. Empty rows are gaps.

    Learn more: [Traceability](think-like-a-tester/test-cases/traceability.md)

[](){ #traceback }**Traceback**
:   What Python prints when something goes wrong, the error at the bottom and the path to it above. Read it from the bottom.

    Learn more: [Errors and exceptions](start-here/python-for-testers/errors-and-exceptions.md)

[](){ #transaction }**Transaction**
:   A group of database changes that are saved together with COMMIT or undone together with ROLLBACK.

    Learn more: [Transactions and clean-up](core-automation/database-testing/transactions-and-cleanup.md)

[](){ #triage }**Triage**
:   Looking at new bugs, checking they are real and clear, and deciding how soon each one gets fixed.

    Learn more: [Severity and priority](think-like-a-tester/bug-reports/severity-and-priority.md)

[](){ #trigger }**Trigger**
:   Code inside the database that runs by itself when a row changes, such as writing a history row when an order's status changes.

    Learn more: [Stored procedures and triggers](core-automation/database-testing/procedures-and-triggers.md)

## U

[](){ #ui }**UI (User Interface)**
:   The part of an app people see and use, like pages, buttons and forms.

    Learn more: [UI automation](core-automation/ui-automation/index.md)

[](){ #unit-test }**Unit test**
:   A small, fast test that checks one piece of code on its own.

    Learn more: [Test levels and the pyramid](think-like-a-tester/test-levels-and-the-pyramid/index.md)

[](){ #user-story }**User story**
:   A short description of a feature from the user's side, like "As a customer, I want to request a refund, so that I get my money back".

    Learn more: [Reviewing user stories](think-like-a-tester/static-testing-and-reviews/reviewing-user-stories.md)

## V

[](){ #variable }**Variable**
:   A name for a value in a program, like the name age for the number 30.

    Learn more: [Variables and types](start-here/python-for-testers/variables-and-types.md)

[](){ #virtual-environment }**Virtual environment**
:   A private folder of Python packages for one project, so projects do not mix up each other's versions.

    Learn more: [Virtual environments and pip](start-here/python-for-testers/virtual-environments-and-pip.md)

## W

[](){ #walkthrough }**Walkthrough**
:   A review where the author takes others through their work, explaining it and taking questions.

    Learn more: [Review types](think-like-a-tester/static-testing-and-reviews/review-types.md)

[](){ #white-box-testing }**White-box testing**
:   Testing with a view of the code inside, for example to see which lines and branches the tests run.

    Learn more: [Statement and branch coverage](think-like-a-tester/test-design-techniques/statement-and-branch-coverage.md)

## X

[](){ #xfail }**xfail**
:   A pytest marker for a test that is expected to fail, usually because of a known bug. The run stays green until the bug is fixed.

    Learn more: [Markers](core-automation/pytest-framework/markers.md)

<!-- END glossary -->

Missing a word? [Tell us which one](https://github.com/myopensdet/myopensdet.github.io/issues/new?template=content-error.yml&title=Glossary%3A%20add%20a%20word)
and we will add it.
