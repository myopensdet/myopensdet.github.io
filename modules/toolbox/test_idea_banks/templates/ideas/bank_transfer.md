<!-- Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/ -->
# Bank transfer: test ideas

## Works as it should

- Send money to a saved payee and a new payee: both balances change by the exact amount
- The transfer shows in history for both sides, with the same reference
- Scheduled and repeating transfers run on the right day
- Fees are shown before confirming, and charged once

## Refuses bad input

- More than the balance, and more than the daily limit
- Zero, negative amounts, and more decimals than the currency has
- Invalid account number or IBAN (wrong check digits)
- Sending to your own same account

## Edges and limits

- Exactly the balance, and exactly the daily limit
- A scheduled transfer on a weekend, a bank holiday, or the 31st of a short month
- Cancel a scheduled transfer just before it runs
- Two transfers at the same moment that together go over the balance (only one may pass)
- Currency conversion: the rate shown is the rate used, and rounding is right

## Security

- A new payee or a large amount needs extra confirmation (a code, or the app)
- One customer can't send from another customer's account (change the account id)
- The session ends after a short idle time
- Every transfer is in the audit log: who, when, from where

## People, devices and failures

- The connection drops after confirming: the transfer happens once, and the user can see if it did
- The other bank is down or refuses: money comes back, with a clear message
- Amounts are read correctly by a screen reader
