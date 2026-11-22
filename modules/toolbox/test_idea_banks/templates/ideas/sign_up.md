<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Sign-up: test ideas

## Works as it should

- Sign up with every required field, and the account works straight away (or after the email link)
- The welcome or confirmation email arrives, with the right name and a working link
- Optional fields can be left empty
- The new user can log in with the password they chose

## Refuses bad input

- An email that's already used: a clear message (check what it tells a stranger, see Security)
- Same email in another case (Sam@example.com and sam@example.com) counts as the same
- Invalid emails: no @, two @, spaces, a missing domain
- Password rules: one character below the minimum, exactly the minimum, each missing rule
- Password and "repeat password" don't match
- Terms not accepted, when they must be
- Age or date of birth below the allowed age

## Edges and limits

- Names with accents, apostrophes and other alphabets (O'Brien, José, আরশাদ)
- Very long names and emails, up to the database limit
- Double-click the Sign up button: only one account is made
- The confirmation link is used twice, used after it expires, or opened on another device
- Sign up, don't confirm, sign up again with the same email

## Security

- The password is stored as a hash: ask, or check the database (never plain text)
- Robots: a CAPTCHA or rate limit stops thousands of sign-ups
- Hidden fields like role=admin in the request are ignored
- Script tags in the name don't run anywhere the name is shown later

## People, devices and failures

- Every field has a visible label, and errors are next to the field
- The form keeps what you typed after an error
- On a phone: the email field opens the email keyboard
- The email service is down: the account is still made, and the email can be sent again
