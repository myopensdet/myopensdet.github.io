<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Cart and checkout: test ideas

## Works as it should

- Add one item, two of the same item, and different items: the total is right
- Change the quantity and remove items: the total updates
- Tax, shipping and discount are each correct, and in the right order
- The order confirmation, the email and the database show the same items and total
- Stock goes down after the order

## Refuses bad input

- Quantity 0, negative, decimals, letters, and above the stock
- An expired, used or unknown discount code
- Two discount codes, when only one is allowed
- A missing or invalid delivery address

## Edges and limits

- The cart is kept after logging out and in, and after closing the browser
- A guest cart is joined with the user's cart when they log in
- The price changes while the item is in the cart: which price is charged?
- The item sells out while it's in someone's cart
- Totals with cents: 0.1 + 0.2, rounding of tax and discounts
- The minimum order value: one cent below and exactly at it
- Double-click "Place order": only one order
- Back button after paying, and refreshing the confirmation page

## Security

- Changing the price or total in the request is ignored: the server works it out again
- One user can't see or change another user's cart (change the id in the address)
- Discount codes can't be guessed quickly (rate limiting)

## People, devices and failures

- Payment fails: the order isn't placed, the cart is kept, and the user can try again
- The connection drops after paying: the order exists once, not zero or two times
- Two tabs with the same cart: change one, then check out in the other
- The whole checkout works with only a keyboard, and on a phone
