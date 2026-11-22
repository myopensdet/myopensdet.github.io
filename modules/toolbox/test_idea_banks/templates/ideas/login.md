<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Login: test ideas

## Works as it should

- Log in with a correct email and password, and land on the right page
- Email in a different case (ARSHAD.TEST@example.com) still logs in
- "Remember me" keeps you logged in after closing the browser; without it, you're logged out
- Log out, then press Back: no private page is shown
- After login, you return to the page you first asked for, not always the home page
- Log in on two devices at once: both work, or the rule says which one is logged out

## Refuses bad input

- Wrong password, unknown email: the same message for both ("email or password is wrong")
- Empty email, empty password, both empty
- Spaces before or after the email (pasted text)
- Password with the wrong case is refused

## Edges and limits

- Locked after N wrong tries: check the exact N, the message, and when it unlocks
- Expired password: asks for a new one, and the old one stops working
- Session timeout: after the idle time, the next click asks to log in again, and unsaved work is handled
- An account that isn't activated, or was disabled, can't log in, with a clear message
- Password reset link: works once, expires, and an old link stops working after a new one is sent

## Security

- The password is never in the address, the logs, or the page source
- The login page is only on https
- The session cookie has Secure and HttpOnly, and changes after login
- Log out really ends the session: the old cookie or token is refused by the server
- Reset password says the same thing whether the email exists or not
- Many fast tries are slowed down or blocked (rate limiting)

## People, devices and failures

- The password manager fills both fields, and pasting a password works
- Works with only a keyboard: Tab order, Enter submits
- Error messages are read by a screen reader
- Show password button works, and hides it again
- Login service slow or down: a clear message, no blank page
