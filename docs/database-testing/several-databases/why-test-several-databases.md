---
title: "Why Test Several Databases? Multi-Database Testing Explained"
description: "When one app or one company uses PostgreSQL, MySQL, SQLite and MongoDB together, what can go wrong between them, and what a multi-database test suite checks."
level: Intermediate
tags:
  - Database
  - Test design
nav_title: "Why test several databases"
order: 10
summary: "Where several databases meet, and the bugs that live in between."
updated: "2026-11-22"
---

# Why Test Several Databases? Multi-Database Testing Explained

Few companies use one database. The shop's orders live in PostgreSQL. An old system still writes to MySQL. The mobile app keeps an offline copy in SQLite. Product reviews sit in MongoDB. Data moves between them through copy jobs, migrations and reports. Each database on its own can be fine, and the data can still go wrong **between** them.

## What you will learn

- Where several databases show up at work
- The four kinds of bug that live between databases
- What a multi-database test suite checks, in order

## Why this matters at work

"The report says 4 orders in November, the shop says 5." When numbers disagree between systems, someone has to find out which one is right, and why. A test suite that runs the same checks on every database, and compares them, answers that in seconds instead of days.

## The idea in plain words

!!! info "In plain words"
    Think of four shops in a chain, each keeping its own stock book. Each book can look tidy. The trouble is between them: a box sent from one shop that never arrives in the other's book, or arrives with the wrong count. Multi-database testing checks the books against each other.

## Step by step

1. **Know where several databases appear.** The common cases:

    | Situation | Example |
    | --- | --- |
    | Migration | Moving from MySQL to PostgreSQL |
    | Copy for reports | Orders copied every night to a reporting database |
    | Different jobs, different databases | Orders in PostgreSQL, reviews in MongoDB |
    | One product, several databases | Customers choose PostgreSQL or MySQL when they install it |
    | Offline copy | The mobile app keeps orders in SQLite |

2. **Know the four kinds of bug between databases.** Each comes with a real example from this topic:

    - **Rows lost or doubled.** A copy job skipped cancelled orders "because the report doesn't need them". The count is 7 where it should be 8.
    - **Values changed on the way.** A long name cut to 30 letters. A time written in Dhaka time into a column everyone reads as UTC, so an order moved to the next month.
    - **Types that differ.** The same price comes back as `Decimal('49.50')`, `49.5` or `Decimal128`. Naive comparisons report differences that aren't real. Worse, they hide real ones.
    - **The same question asked differently.** "Orders per month" is `to_char` in PostgreSQL, `DATE_FORMAT` in MySQL and a pipeline in MongoDB. Three queries, three chances to get it wrong.

3. **Know what the suite checks, in order.** Cheapest first:

    1. **Schema:** every database has the tables and columns the app expects.
    2. **Integrity:** on each database, the same rules hold: unique emails, no orders without a customer.
    3. **Counts:** every table has the same number of rows as in the source.
    4. **Checksums:** a fingerprint of each whole table matches the source.
    5. **Values:** when a fingerprint differs, exactly which rows and fields differ.

    The [template project](index.md#templates) does all five on PostgreSQL, MySQL, SQLite and MongoDB, with one set of tests.

    !!! success "Check: you should now be able to"
        Name where several databases show up at work, the four kinds of bug between them, and the five checks in order.

## When it goes wrong

- **Every system says it's right.** Each team checks only its own database. Agree on one **source of truth** for each kind of data, and compare everything else against it.
- **The numbers differ, but nobody knows since when.** Nothing compared them. Run the comparison every night, not only after a migration.
- **The comparison reports thousands of differences.** Usually a type difference, not a data one: `49.5` against `49.50`, or the same time in two time zones. See [cross-database comparison](cross-database-comparison.md).

## Common mistakes

!!! warning "Common mistakes"
    - **Testing only the source database.** The bug is in the copy.
    - **Comparing only row counts.** A copy that cuts every name to 30 letters has the right count.
    - **Writing four test suites, one per database.** They drift apart. One suite, run on every database.

## Try it yourself

Your company copies orders from PostgreSQL to MySQL every night for the finance reports. List three things that could go wrong in the copy, and how you'd notice each.

??? success "Solution"
    Any three of these:

    - Rows lost (a filter, a crash halfway): compare row counts.
    - Text cut or letters broken (column too short, wrong character set): compare values, and test names with accents.
    - Times shifted (time zones): compare values, and a per-month report on both sides.
    - Money rounded (float instead of decimal): compare values with a checksum.
    - Rows doubled (the job ran twice): compare row counts, and look for duplicate ids.

## Quick check

1. Why isn't a matching row count enough?

    ??? question "Answer"
        Values can change while the count stays the same, like names cut short.

2. What's a source of truth?

    ??? question "Answer"
        The one database everyone agrees is right for that data. The others are compared against it.

3. Why one test suite instead of one per database?

    ??? question "Answer"
        Separate suites drift apart, and then you're comparing tests, not data.

## References

- [PostgreSQL documentation](https://www.postgresql.org/docs/17/index.html)
- [MySQL 8.4 reference manual](https://dev.mysql.com/doc/refman/8.4/en/)
- [SQLite documentation](https://www.sqlite.org/docs.html)
- [MongoDB manual](https://www.mongodb.com/docs/manual/)

Written for PostgreSQL 17, MySQL 8.4, SQLite 3 and MongoDB 8.0. Links checked: November 2026.
