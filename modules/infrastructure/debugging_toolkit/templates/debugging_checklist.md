<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->

# Debugging checklist: a test failed

1. **Read the last lines first.** The summary says which tests failed. In each failure,
   the `E` lines say what was wrong; the last `file:line` says where it broke.
2. **Run that one test alone.** `pytest "tests/test_x.py::test_name"` (or `-k name`).
   - Fails the same way: the problem is in that test or the code it calls.
   - Passes, or fails differently: **something shared** (data, a list, a file, the order of tests).
3. **Make it fail fast, again and again.** `pytest --lf -x` reruns only failures and stops at the first.
4. **See more.** `-l` shows local variables (careful: tokens too). `--log-cli-level=DEBUG` shows the app's logs.
5. **Stop at the failure and look around.** `pytest --pdb`, then `p <name>`, `pp <name>`, `q`.
6. **Look at the real request.** `curl -v <url>`, or the browser's developer tools (F12): Network and Console.
7. **Check what changed.** `git log -5`, `git diff`: a new release, new test data, a new environment?
8. **Write down the cause in one sentence** before you fix or report anything.
   "The cart keeps items from the previous test, because every Cart shares one list."
9. **Fix one thing, run everything again.** One bug often hides the next one.
