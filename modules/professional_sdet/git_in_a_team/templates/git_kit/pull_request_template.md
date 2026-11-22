<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
<!-- Save as .github/pull_request_template.md: GitHub fills every new pull request with it. -->

## What changed

<!-- One or two sentences. Link the ticket: "SHOP-420". -->

## Why

## How I checked it

- [ ] Ran the changed tests locally: `python -m pytest tests/<file>` (<N> passed)
- [ ] Saw each new test fail once (changed one expected value, then put it back)
- [ ] The pipeline is green

## What reviewers should look at

<!-- The tricky part, or the decision you're unsure about. -->

## Checklist

- [ ] One change per pull request
- [ ] Test names say what they check
- [ ] No fixed waits (`sleep`); waits for something real
- [ ] No passwords, tokens or real people's data
- [ ] Shared fixtures or helpers changed? Every test that uses them still passes
