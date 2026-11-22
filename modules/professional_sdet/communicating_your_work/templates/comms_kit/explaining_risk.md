<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Explaining a risk to a manager

Managers decide. Your job is to make the decision easy: what could happen, to whom,
how likely, and what the options are. In plain words, with no test jargon.

## The four-line risk message

1. **What could happen:** <in user terms: "Some customers can't see their order page.">
2. **Who and how often:** <"About 1 in 3 order page visits when the site is busy.">
3. **What we know and don't know:** <"Seen on staging under load. Not seen in production yet.">
4. **Options:** <"A) Release now and fix in 2.16. B) Wait two days for the fix. I'd suggest A, because ...">

## Words to avoid, and what to say instead

| Avoid | Say |
| --- | --- |
| "The P95 latency regressed." | "The slowest pages got two times slower." |
| "Flaky." | "Fails sometimes, we're not sure why yet." |
| "Coverage is low." | "We only tested the main path. Refunds in euros weren't tested." |
| "It's fine." / "It's broken." | Give the verdict and one reason: "AMBER: ready if you accept one risk." |
| "We tested everything." | Never true. Say what you tested and what you didn't. |
