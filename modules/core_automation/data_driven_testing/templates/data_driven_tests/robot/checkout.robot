# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
*** Settings ***
Documentation       Keyword-driven: each test is a list of steps anyone on the team can read.
Library             ShopKeywords.py


*** Test Cases ***
Member With A Coupon Pays The Lowest Price
    Start An Order Of    30.00
    Apply Coupon    SAVE10
    Customer Is A Member
    Total Should Be    25.65

Welcome Coupon Needs A Subtotal Of 20
    Start An Order Of    19.99
    Apply Coupon    WELCOME5
    Total Should Be    19.99

Welcome Coupon At Exactly 20
    Order Of 20.00 With WELCOME5 Should Cost 15.00


*** Keywords ***
Order Of ${subtotal} With ${coupon} Should Cost ${expected}
    [Documentation]    A keyword made of other keywords, with its arguments inside its name.
    Start An Order Of    ${subtotal}
    Apply Coupon    ${coupon}
    Total Should Be    ${expected}
