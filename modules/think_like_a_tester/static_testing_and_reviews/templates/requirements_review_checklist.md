<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Requirements review checklist

For longer documents: a spec, a feature description, an API design.
Read once for the big picture, then once with this list.

## Clear

- [ ] Each requirement says one thing (no "and also" hiding a second rule)
- [ ] Words are used the same way everywhere ("order", "basket" and "cart" mean one thing, or are defined)
- [ ] Words like should, fast, easy, etc. are replaced with something testable
- [ ] Every number has a unit and says if the limit is included ("up to and including 120")

## Complete

- [ ] Error cases are described, not only the happy path
- [ ] Every input says what is allowed and what is refused
- [ ] Every status or state lists what can happen next (see the state transition worksheet)
- [ ] Who can do what is written down (roles and permissions)
- [ ] Nothing says "TBD" without an owner and a date

## Consistent

- [ ] No two requirements say different things about the same case
- [ ] It matches the existing system, or says clearly what changes
- [ ] Examples in the document agree with the rules in it

## Testable

- [ ] For each requirement, you can say how to test it in one sentence
- [ ] Things that need a human judgement ("looks good") say who judges and how

## Findings

| # | Where (section, line) | Problem | Type (unclear, missing, conflict, untestable) | Owner |
| --- | --- | --- | --- | --- |
| 1 | <where> | <problem> | <type> | <name or role> |
