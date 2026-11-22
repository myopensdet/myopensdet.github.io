<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Story: refund request (after review)

As a customer, I want to request a refund for items I received, so that I get my money back without calling support.

## Acceptance criteria

1. A customer can request a refund for each item of an order, up to 30 days after delivery, from the "My orders" page.
2. Each item can be refunded once. A second request for the same item is refused with the message "This item was already refunded".
3. A refund request is approved or refused within 2 working days. The customer gets an email in both cases, and a refused request includes the reason.
4. Items bought on sale can be refunded only if they are faulty. The customer must choose "faulty" as the reason.
5. Card and PayPal payments go back to the same account. Gift card payments become store credit.
6. If the original card is expired or closed, the refund becomes store credit, and the customer gets an email saying so.
7. Orders not delivered yet are not refunded here. The page links to "Cancel order" instead.
