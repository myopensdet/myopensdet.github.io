<!-- Template from myOpenSDET: https://myopensdet.github.io/ -->
# Gherkin cheat sheet

Gherkin is the plain-language format of `.feature` files, used by behave, pytest-bdd and Cucumber. Every example here is checked with the official Gherkin parser.

## The keywords

| Keyword | Means |
| --- | --- |
| `Feature:` | What this file is about. One per file |
| `Rule:` | One business rule, with its examples under it (optional) |
| `Background:` | Steps that run before **every** scenario in the file |
| `Scenario:` | One example of the behaviour |
| `Scenario Outline:` + `Examples:` | The same scenario, once for each row of a table |
| `Given` | Where we start: the state before |
| `When` | The one action the user takes |
| `Then` | What should be true after |
| `And`, `But` | More of the step above |
| `@tag` | A label, to run a group: `behave --tags=@smoke`, `pytest -m smoke` |
| `#` | A comment |

## A full example

```gherkin
@checkout
Feature: Discount codes
  Customers can use one discount code per order.

  Background:
    Given I am logged in as "arshad.test@example.com"
    And my cart has a "Practice book" for 24.50

  @smoke
  Scenario: A valid code lowers the total
    When I use the code "SAVE10"
    Then the total is 22.05

  Scenario: An expired code is refused
    When I use the code "OLD2024"
    Then I see the message "This code has expired"
    And the total is 24.50
```

## The same scenario with many values

```gherkin
Feature: Discount codes

  Scenario Outline: Codes and totals
    Given my cart has a "Practice book" for 24.50
    When I use the code "<code>"
    Then the total is <total>

    Examples:
      | code    | total |
      | SAVE10  | 22.05 |
      | HALF    | 12.25 |
      | WRONG   | 24.50 |
```

## Tables and long text in a step

```gherkin
Feature: Orders

  Scenario: An order with several items
    Given my cart has these items:
      | title         | price |
      | Practice book | 24.50 |
      | Test mug      | 9.99  |
    When I place the order
    Then the receipt says:
      """
      Thank you for your order.
      Total: 34.49
      """
```

## Rules

```gherkin
Feature: Passwords

  Rule: A password has at least 12 characters

    Scenario: 11 characters are refused
      When I sign up with a password of 11 characters
      Then I see "Use at least 12 characters"

    Scenario: 12 characters are accepted
      When I sign up with a password of 12 characters
      Then my account is created
```

## Good steps, bad steps

| Bad | Good | Why |
| --- | --- | --- |
| `When I click the button with id "btn-7"` | `When I place the order` | Say **what** the user does, not how. The page can change; the behaviour doesn't |
| `Then it works` | `Then the total is 22.05` | A Then must be checkable |
| Three `When` steps in one scenario | One `When` per scenario | One behaviour per scenario. Split it |
| `Given I open the browser, go to login, type the email...` | `Given I am logged in as "arshad.test@example.com"` | Set-up details belong in the step code |
| Every scenario repeats the same Givens | Put them in `Background:` | Shorter, and one place to change |
