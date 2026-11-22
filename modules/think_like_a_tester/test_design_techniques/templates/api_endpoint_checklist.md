<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# API endpoint test checklist

For any endpoint. Tick what you checked. Write "n/a" and a reason for what doesn't apply.

## Happy path

- [ ] A correct request gives the right status code (200, 201, 204) and body
- [ ] The response has every field the docs promise, with the right types
- [ ] The change is really saved (read it back, or check the database)

## Bad input

- [ ] A missing required field gives 400 or 422, and says which field
- [ ] Wrong types (text for a number), and values past each limit
- [ ] Extra unknown fields: ignored or refused, as the docs say
- [ ] Empty body, and a body that is not valid JSON

## Who can do it

- [ ] No login token gives 401
- [ ] A valid token for a user without permission gives 403
- [ ] One user can't read or change another user's data (try their ID)

## Repeat and timing

- [ ] Sending the same request twice doesn't create two of something (orders, payments)
- [ ] Very large lists are split into pages, and the page limits are checked

## Errors and safety

- [ ] Errors never show stack traces, SQL or server paths
- [ ] Rate limits, if any, give 429 with a clear message
- [ ] The response doesn't include private fields (password hashes, internal IDs)
