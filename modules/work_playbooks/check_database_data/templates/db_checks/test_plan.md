<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Database test plan: shop database

Fill this in before you write checks. Post it in the ticket so the team can check it.

## 1. Access

| Question | Answer |
| --- | --- |
| Which database (test environment) | `shop` on `127.0.0.1:58232` |
| Type | PostgreSQL 17 |
| User | A **read-only** user, from the team. Never written in a file |
| Who owns the data (to ask questions) | ? |
| Is there real customer data in it? | ? (if yes: never copy rows into tickets or reports) |

## 2. Tables to check

| Table | What it holds | Linked to | Rules the app expects |
| --- | --- | --- | --- |
| `customers` | People who order | - | email unique, ignoring case |
| `products` | Things to buy | - | price above 0; stock 0 or more |
| `orders` | One per checkout | `customers` | status is one of: new, paid, shipped, delivered, cancelled; total = sum of its items |
| `order_items` | Lines of an order | `orders`, `products` | every line belongs to an existing order |

## 3. Checks

| Kind | Checks | Done |
| --- | --- | --- |
| Saved correctly | After an API/UI test creates an order: the order row, its items, its total | [ ] |
| Data quality | Duplicates, orphans, wrong totals, unknown values, numbers out of range | [ ] |
| Structure | Tables exist; columns and types; foreign keys | [ ] |

## 4. Questions for the team

1. `orders.customer_id` has no foreign key. Is that on purpose?
2. Can one person have two accounts with the same email in different case?

## 5. Not in this plan

- Speed of queries
- Backups and restore
