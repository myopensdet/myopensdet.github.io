<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Payments: test ideas

Use the payment provider's test mode and test card numbers. Never a real card.

## Works as it should

- Each payment method the app offers: card, wallet, bank, voucher
- The amount and currency the provider receives match the order
- A full refund, a partial refund, and several partial refunds up to the full amount
- Receipts and invoices show the right amounts, tax and date

## Refuses bad input

- Declined card, expired card, wrong security code (the provider's test cards for each)
- Not enough money
- A refund bigger than what's left to refund
- A currency the app doesn't support

## Edges and limits

- Extra checks like 3-D Secure: passed, failed, and closed by the user
- Amounts with cents, very small and very large amounts, currencies with no cents (JPY) or three decimals
- The provider's answer is slow, or arrives twice (webhooks are sent again)
- The provider says "paid" but the app's page timed out: the order still completes
- Paying twice for the same order is stopped, or refunded

## Security

- Card numbers never reach your server, logs or database (the provider's form handles them)
- The success page can't be opened directly to mark an order paid
- Webhooks from anyone except the provider are refused (signature check)
- Refunds need the right role

## People, devices and failures

- The payment form is usable with a screen reader and a keyboard
- The provider is down: a clear message, and the order waits safely
- Money in the app, the provider's dashboard and the accounting export agree at the end of the day
