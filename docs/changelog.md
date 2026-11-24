---
title: "What's New on myOpenSDET"
description: "Every new topic, lesson and template added to myOpenSDET, newest first."
updated: "2026-11-24"
---

# Changelog

## Unreleased

### November 2026

- **New guide: [Testing microservices](api-testing/microservices/index.md).** A practice shop of three small services (orders, stock, payments) that runs on your computer or in Docker Compose. It tests one service alone with fakes, then the calls between services with faults switched on (down, slow, declined), and follows one request through every service with a request id. A planted bug, items never given back after a failed payment, is caught at both levels.
- **New guide: [GraphQL testing](api-testing/graphql/index.md).** A small Python kit (only `requests` and pytest) that tests queries, mutations, variables and errors, never misses an error hidden behind a `200`, and checks the schema for removed or changed fields. It shows two real bugs in a public practice API, and a public API whose errors leak its internal address.
- **API Testing lessons rebuilt.** The ten core lessons, from [How HTTP works](api-testing/how-http-works.md) to [An API client class](api-testing/api-client-class.md), now follow the same layout as the Python lessons: a diagram, real output, line by line, real QA use, a task with a solution, and real errors. They also show real bugs found in the public demo APIs while the pages were written, like an id of `1.5` returning another booking, and a server that crashes on a wrongly shaped login header.
- **Python lessons rewritten.** All ten lessons from [Variables and data types](programming-for-testers/variables-and-data-types.md) to [Virtual environments and pip](programming-for-testers/virtual-environments-and-pip.md) now use real test data (device IDs, status codes, API responses), with a diagram, a line-by-line explanation, real output, a task with a solution, and real error messages.
- **New name and address.** The site is now myOpenSDET, at `myopensdet.github.io`. Old addresses forward to the new pages.
- **Learning categories.** The home page shows one card per category, and each category lists its lessons in the order to learn them. Planned categories are on the [Roadmap](roadmap.md).
- **Easier to read.** One type scale on every screen size: 17px body text, clear headings.
- **Safer.** Every page has a Content-Security-Policy, and the site has no analytics or tracking.
- Site skeleton and skills matrix.
