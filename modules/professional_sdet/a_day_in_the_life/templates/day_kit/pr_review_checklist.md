<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Reviewing a pull request as a tester

## App code (a developer's change)

- [ ] I understand what changed and why (read the ticket first)
- [ ] There are tests for it, and they would fail without the change
- [ ] Error cases are handled: empty, too long, wrong type, no permission
- [ ] Nothing obvious for security: no secrets, input is checked, logs don't print passwords
- [ ] The pipeline is green
- [ ] I asked questions as questions: "What happens when the list is empty?"

## Test code (a colleague's tests)

- [ ] The test name says what it checks
- [ ] Each test checks something real (not just "status is 200")
- [ ] No fixed waits (`sleep`); it waits for something to happen
- [ ] No shared data between tests; it can run alone and in any order
- [ ] No passwords, tokens or real people's data in the code
- [ ] It ran in the pipeline, and I saw it fail once (change one value and run it)
