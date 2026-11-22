# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: variables and data types. Run: python types_demo.py"""

# 1. One API check, kept in variables.
device_id = "SNS-0042"  # str: an ID is text, even when it has digits
expected_status = 200  # int: status codes are whole numbers
actual_status = 200
response_time = 0.45  # float: seconds, with a decimal point
max_response_time = 1.0
firmware = None  # None: the API did not send a firmware version

test_passed = actual_status == expected_status and response_time <= max_response_time

print(type(device_id), type(actual_status), type(response_time))
print(type(test_passed), type(firmware))
if test_passed:
    print(f"PASS: {device_id} answered {actual_status} in {response_time}s")
else:
    print(f"FAIL: {device_id} expected {expected_status}, got {actual_status}")

# 2. Text that looks like a number is still text.
status_from_csv = "200"  # CSV files, forms and URLs give you text
print(status_from_csv == 200, int(status_from_csv) == 200)

# 3. Decimals are not exact. Compare money in whole cents.
item_prices = 0.10 + 0.20
print(item_prices, item_prices == 0.30)
print(10 + 20 == 30, round(item_prices, 2) == 0.30)

# 4. None means "no value". Check it with "is None".
print(firmware is None)
