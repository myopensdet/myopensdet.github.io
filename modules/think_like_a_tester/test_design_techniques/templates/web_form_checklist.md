<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Web form test checklist

For any form: sign-up, checkout, contact, search. Tick what you checked, write "n/a" and a reason
for what doesn't apply, and keep a copy with the test plan, so people can see what was checked.

## Fields

- [ ] Every required field refuses empty, and says which field is missing
- [ ] Each field's limits: the edges and one past (see the groups and edges worksheet)
- [ ] Spaces before and after are handled the same way everywhere
- [ ] Paste works, and pasted text with extra spaces is handled
- [ ] Autofill from the browser fills the right fields

## Errors

- [ ] The error appears next to the field it belongs to
- [ ] The message says how to fix it ("Use 8 or more characters"), not only "Invalid"
- [ ] Fixing the field removes the error
- [ ] What you typed is still there after an error (except passwords)

## Sending

- [ ] Double click on Submit sends only once
- [ ] A slow server shows that something is happening
- [ ] Back after sending doesn't send again, or warns first
- [ ] The same rules are checked on the server, not only in the browser

## Everyone can use it

- [ ] Every field has a visible label (not only placeholder text)
- [ ] The whole form works with the keyboard alone (Tab, Enter, Space)
- [ ] Errors are read out by a screen reader
- [ ] It works on a phone-sized screen, and the right keyboard opens (numbers, email)

## Safety

- [ ] HTML typed into a field shows as text later, never runs
- [ ] Password fields hide the text, and allow paste and password managers
- [ ] Error messages don't reveal private facts ("this email has an account")
