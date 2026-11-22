# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
*** Settings ***
Documentation       Data-driven: one keyword, one row of data per test.
...                 The same cases as test_data/signup_cases.csv.
Library             ShopKeywords.py
Test Template       Signup Problems Should Be


*** Test Cases ***                  EMAIL                   PASSWORD            AGE     EXPECTED
Valid adult                         arshad@example.com      correct-horse-1     30      ${EMPTY}
Exactly 18
    [Tags]    known-bug
                                    maria@example.com       correct-horse-1     18      ${EMPTY}
One day under 18                    zoe@example.com         correct-horse-1     17      age
Password 7 characters               lee@example.com         short12             25      password
Password 8 characters               lee@example.com         short123            25      ${EMPTY}
Email without @                     arshad.example.com      correct-horse-1     30      email
Everything wrong                    not-an-email            short               12      email password age
