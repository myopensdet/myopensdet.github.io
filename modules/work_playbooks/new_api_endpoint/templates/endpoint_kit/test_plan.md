<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Test plan: `POST /carts/add`

Copy this file for each new endpoint. Fill in what you know, and turn every "?" into a
question for the developer or product owner. Keep it short: one page.

## 1. What it is

| | |
| --- | --- |
| Endpoint | `POST /carts/add` |
| What it does, in one sentence | Creates a cart for a user with the products and quantities sent |
| Ticket | ? |
| Who calls it | The web shop's "Add to cart" button; maybe the mobile app? |
| Environment to test on | Staging: `https://...` |
| How to log in | ? (token, from where, how long it lives) |
| Developer to ask | ? |
| Deadline | ? |

## 2. Rules (what must be true)

Write each rule so a test can check it. Mark where it came from: ticket, developer, docs, or
"my guess, to confirm".

- [ ] A valid cart answers `201` with the cart, its products and a total (ticket)
- [ ] `total` = price x quantity, summed over products (my guess, to confirm)
- [ ] `userId` is required, and must be a number (seen in the probe, to confirm)
- [ ] `products` must not be empty (seen in the probe)
- [ ] `quantity` must be a whole number, 1 or more (my guess, to confirm)
- [ ] An unknown product id is refused, not ignored (my guess, to confirm)
- [ ] Refusals answer `400` with a message that says why (my guess, to confirm)

## 3. What to test

| Area | Checks | Done |
| --- | --- | --- |
| Happy path | Valid body; several products; the largest normal order | [ ] |
| Required fields | Each one missing, `null`, empty | [ ] |
| Types | Text where a number goes; a number where text goes; a list where one value goes | [ ] |
| Boundaries | 0, 1, -1, the largest allowed, one more than the largest | [ ] |
| References | An id that doesn't exist; an id of something deleted; someone else's id | [ ] |
| Duplicates | The same item twice in one request; the same request sent twice | [ ] |
| Format | Not JSON; empty body; wrong `Content-Type` | [ ] |
| Access | No token; expired token; a user who isn't allowed | [ ] |
| Side effects | What is saved in the database; emails or events sent; stock changed | [ ] |
| Speed | Normal answer time; the largest order | [ ] |

## 4. Questions for the team

1. Is a quantity of 0 refused, or changed to 1?
2. Is there a largest quantity?
3. The same product twice: merged into one line, or refused?
4. Is the cart saved? Where can I check it?

## 5. Not testing, and why

- Load testing: separate task.
- The web page's button: covered by the UI tests.
