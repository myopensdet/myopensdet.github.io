# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: functions. Run: python functions_demo.py"""


def is_valid_reading(temperature: float | None, low: float = -20.0, high: float = 60.0) -> bool:
    """True when a temperature reading is there and inside the allowed range."""
    if temperature is None:
        return False
    return low <= temperature <= high


def make_device(device_id: str, status: str = "online", battery: int = 100) -> dict:
    """Fake test data for one device. Change only what your test cares about."""
    return {"id": device_id, "status": status, "battery": battery}


def check_response(
    device_id: str,
    actual_status: int,
    seconds: float,
    expected_status: int = 200,
    max_seconds: float = 1.0,
) -> str:
    """One line for the test report: PASS, or FAIL with the reason."""
    if actual_status != expected_status:
        return f"FAIL: {device_id} expected {expected_status}, got {actual_status}"
    if seconds > max_seconds:
        return f"FAIL: {device_id} took {seconds}s (limit {max_seconds}s)"
    return f"PASS: {device_id} answered {actual_status} in {seconds}s"


def log_result(line: str) -> None:
    """Print a report line. It returns nothing."""
    print(f"[report] {line}")


print(is_valid_reading(21.5), is_valid_reading(85.0), is_valid_reading(None))
print(is_valid_reading(85.0, high=90.0))
print(make_device("SNS-0042"))
print(make_device("SNS-0043", battery=5))
print(check_response("SNS-0042", 200, 0.45))
print(check_response("SNS-0043", 503, 0.12))
print(check_response("SNS-0044", 200, 2.4))

returned = log_result("3 devices checked")
print(returned)

# A function that returns a value is easy to test: try the edges of the range.
print(is_valid_reading(60.0), is_valid_reading(60.1), is_valid_reading(-20.0))
