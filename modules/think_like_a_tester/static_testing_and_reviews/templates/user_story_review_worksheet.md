<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# User story review

Fill this before the story is planned, ideally with the product owner and a developer.
Every "no" and every question is cheaper to fix now than after the code exists.

## The story

- **Story:** <link or title>
- **Reviewed by:** <names or roles> · **Date:** <date>

## 1. Who, what and why

- [ ] It says who the user is (customer, admin, guest), not just "the user"
- [ ] It says what they want to do, in one sentence
- [ ] It says why, so we can tell if a solution really helps

## 2. Acceptance criteria

- [ ] Every criterion can be checked with a clear pass or fail
- [ ] Numbers have units and limits ("within 5 working days", "up to 10 items")
- [ ] No vague words left (run `python ambiguity_scan.py story.md`)
- [ ] Each criterion says what the user sees, including on failure

## 3. Missing cases

- [ ] What happens when it goes wrong? (errors, refusals, timeouts)
- [ ] What happens at the limits? (first, last, zero, maximum)
- [ ] What about other states? (cancelled, already done, logged out)
- [ ] Who must NOT be able to do it?
- [ ] What happens to existing data and existing users?

## 4. Fits with the rest

- [ ] It doesn't break or contradict an earlier story or rule
- [ ] Other teams or systems it touches are named (payments, email, reports)
- [ ] Speed, security and accessibility needs are written down, or marked "none"

## Questions for the product owner

| # | Question | Answer | Story updated? |
| --- | --- | --- | --- |
| 1 | <question> | <answer> | <yes / no> |

## Result

- [ ] Ready to plan
- [ ] Ready after the answers above are added to the story
- [ ] Not ready: <reason>
