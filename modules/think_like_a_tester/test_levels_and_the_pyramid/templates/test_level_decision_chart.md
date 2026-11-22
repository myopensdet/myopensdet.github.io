<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Which test level? A decision chart

Use this for every new test idea. Go down the questions in order and stop at the first "yes".
The goal: test each thing at the lowest level that can really catch the bug.

## The questions

1. **Is it a rule inside one function or class?** (a price, a date, a validation)
   Yes: write a **unit test**.
2. **Is it about parts of our code working together?** (the cart using the coupon rules, code saving to the database)
   Yes: write an **integration test**.
3. **Is it about what our API accepts and answers?** (status codes, fields, errors, permissions)
   Yes: write an **API test**.
4. **Can it only be seen in the browser?** (a button, a layout, a page that needs JavaScript)
   Yes: write a **UI test**.
5. **Is it a full journey that earns money or keeps users safe?** (sign up, buy, pay, reset a password)
   Yes: write **one end-to-end test** for the happy path. Test the details lower down.

## Also ask

- Is it about speed, many users, or staying up? Add a **performance or reliability** test (see the non-functional lesson).
- Does it need a human to judge it? ("Is this easy to use?", "Does it look right?") Keep it a **manual or exploratory** check.

## My test ideas

| Test idea | Level | Why this level |
| --- | --- | --- |
| <idea> | <unit / integration / api / ui / e2e> | <reason> |
| <idea> | <level> | <reason> |

## Check the shape

- [ ] Most of my new tests are unit or integration tests
- [ ] Each UI or end-to-end test checks something no lower test can
- [ ] I did not test the same detail at three levels
