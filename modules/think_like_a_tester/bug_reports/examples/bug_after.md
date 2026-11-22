<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Sign-up refuses usernames in Bengali, but accepts accented Latin names

## Summary

The username rule refuses every name written in Bengali, like "আরশাদ", with "Username can only use letters and numbers". Names with accents, like "José", are accepted. Bengali-speaking customers can't sign up with their own name.

## Steps to reproduce

1. Open the sign-up form on the test environment.
2. Enter the username "আরশাদ" and age 30.
3. Press "Create account".

## Expected result

The account is created. The rule says "letters and numbers only". "আরশাদ" is made of Bengali letters, and accented Latin letters like "é" are already accepted, so Bengali names should be too. If the team decides only some alphabets are allowed, the rule needs to say which ones.

## Actual result

The form shows "Username can only use letters and numbers", and no account is created. The same steps with "José" create the account.

## Environment

- Version or build: example shop, test design techniques topic
- Where: local
- Browser and device, or API client: Python 3.13, `check_signup()` called directly
- Test account or data: username "আরশাদ", age 30 (test data only)

## Severity and priority

- Severity: major, because every customer with a Bengali name is blocked from signing up
- Suggested priority: high, because many of our customers write their names in Bengali

## Evidence

- `python try_guesses.py` output: "a Bengali name    Username can only use letters and numbers" and "an accent    accepted"
- Cause found: Python's `str.isalnum()` returns False for the Bengali vowel sign "া"

## Notes

- Happens every time, for any Bengali name with a vowel sign.
- Related: names that look like "admin" in wide letters are accepted (separate report).
