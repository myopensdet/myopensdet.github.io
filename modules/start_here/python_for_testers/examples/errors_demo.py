# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: exception handling. Run: python errors_demo.py"""

import json


class ReadingError(Exception):
    """A device sent a reading that the system must not accept."""


def parse_reading(payload: str) -> float:
    """Turn one device message into a temperature. Raise ReadingError if it is wrong."""
    try:
        data = json.loads(payload)
        temperature = float(data["temperature"])
    except json.JSONDecodeError:
        raise ReadingError(f"not JSON: {payload!r}") from None
    except KeyError:
        raise ReadingError(f"no temperature field: {payload!r}") from None
    except (TypeError, ValueError):
        raise ReadingError(f"temperature is not a number: {payload!r}") from None
    if not -20 <= temperature <= 60:
        raise ReadingError(f"{temperature} is out of range: {payload!r}")
    return temperature


# Messages as they arrive from devices (for example over MQTT). Some are broken.
messages = [
    '{"device": "SNS-0042", "temperature": 21.5}',
    '{"device": "SNS-0043", "temperature": "hot"}',
    '{"device": "SNS-0044"}',
    "temperature=19",
    '{"device": "SNS-0045", "temperature": 85}',
]
accepted = []
rejected = []
print("connected to the broker (pretend)")
try:
    for message in messages:
        try:
            accepted.append(parse_reading(message))
        except ReadingError as error:
            rejected.append(str(error))
finally:
    print("disconnected from the broker")  # runs even if the loop crashes

print("accepted:", accepted)
for reason in rejected:
    print("rejected:", reason)
