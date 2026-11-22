<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# SHOP-420: Discount code at checkout (after refinement)

As a signed-in shopper, I want to use a discount code at checkout, so that I pay less.
Guests can't use codes in this story (SHOP-431 covers guests).

## Acceptance criteria

1. Given a cart of 40.00 and the code SAVE10 (10% off), when I apply it, then the total is 36.00.
2. Given the code SAVE10 has expired, when I apply it, then the total stays 40.00 and I see "This code has expired".
3. Given the code field is empty, when I press Apply, then nothing changes and I see "Enter a code".
4. Given SAVE10 is already applied, when I apply SAVE10 again, then the total stays 36.00 and I see "Code already applied".
5. Given any code, the new total shows within 1 second.
6. Only one code per order. Codes are at most 20 characters.
