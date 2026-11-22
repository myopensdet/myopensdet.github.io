<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Stand-up update (copy, fill, say it in under a minute)

**Done:** <ticket>: <what is now tested or reported>
**Today:** <ticket>: <what I'll test or automate>
**Nightly run:** <N> new failures: <one line each, with the ticket if raised>
**Blocked / risk:** <what stops me, and who can unblock it> (or "nothing")

Example:

**Done:** SHOP-398: checkout with vouchers tested, 6 API tests merged, 1 bug raised (SHOP-415).
**Today:** SHOP-401: order history. Asking about the sort order first.
**Nightly run:** 2 new: discount code not applied (raised SHOP-416), order history order (checking if the test is wrong).
**Blocked / risk:** the test environment's payment provider is slow again (SHOP-412). Release tests for payments can't finish until it's fixed.
