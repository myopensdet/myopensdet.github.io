# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
Feature: Shopping cart
  As a shopper
  I want to put books in my cart
  So that I know what I will pay before I order

  Background:
    Given an empty cart

  @smoke
  Scenario: One book
    When I add 1 copy of "Python for Testers"
    Then the cart total is 24.99

  Scenario: Two different books
    When I add 1 copy of "Python for Testers"
    And I add 2 copies of "SQL in a Week"
    Then the cart total is 63.99

  Scenario Outline: Several copies of one book
    When I add <copies> copies of "<book>"
    Then the cart total is <total>

    Examples:
      | copies | book               | total  |
      | 2      | Python for Testers | 49.98  |
      | 3      | SQL in a Week      | 58.50  |
      | 10     | SQL in a Week      | 195.00 |

  Scenario: More than 10 copies is refused
    When I add 11 copies of "SQL in a Week"
    Then I see the message "You can add 1 to 10 copies"
    And the cart total is 0.00
