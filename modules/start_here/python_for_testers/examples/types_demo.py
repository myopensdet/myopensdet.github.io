# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Lesson: variables and types. Run: python types_demo.py"""

username = "arshad"  # str: text
age = 30  # int: a whole number
price = 4.25  # float: a number with a decimal point
in_stock = True  # bool: True or False
coupon = None  # None: "nothing here yet"

print(type(username), type(age), type(price), type(in_stock), type(coupon))
print(f"{username} is {age}, the notebook costs {price}")

# Text that looks like a number is still text. Forms and APIs often send text.
age_from_form = "30"
print(age_from_form == 30, int(age_from_form) == 30)

# Floats are not exact. Never compare money with ==.
print(0.1 + 0.2, 0.1 + 0.2 == 0.3)
print(round(0.1 + 0.2, 2) == 0.3, 10 + 20 == 30)  # or use whole cents
