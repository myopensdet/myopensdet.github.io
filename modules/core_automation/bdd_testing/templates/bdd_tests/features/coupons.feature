# Template from myOpenSDET: https://myopensdet.github.io/
Feature: Coupons
  As a shopper
  I want to use a coupon
  So that I pay less

  The shop knows one coupon, SAVE10, and an order can use it only once.

  Background:
    Given an empty cart
    And I add 2 copies of "Python for Testers"

  @smoke
  Scenario: SAVE10 takes 10% off
    When I apply the coupon "SAVE10"
    Then I see the message "Coupon SAVE10 applied"
    And the cart total is 44.98

  Scenario: An unknown coupon changes nothing
    When I apply the coupon "FREE"
    Then I see the message "Unknown coupon: FREE"
    And the cart total is 49.98

  @known_bug
  Scenario: A coupon works only once
    Bug COUPON-TWICE: the second use takes another 10% off.

    When I apply the coupon "SAVE10"
    And I apply the coupon "SAVE10"
    Then I see the message "Coupon SAVE10 is already applied"
    And the cart total is 44.98
