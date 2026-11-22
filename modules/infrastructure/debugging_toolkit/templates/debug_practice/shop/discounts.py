# Template from myOpenSDET: https://myopensdet.github.io/
"""Discount codes. Practice code with planted bugs: don't copy it into real work."""

import logging

log = logging.getLogger(__name__)

CODES = {"WELCOME10": 10, "BOOKS20": 20}


def percent_off(code: str | None) -> int:
    if code is None:
        return 0
    log.debug("looking up discount code %r", code)
    return CODES[code.upper()]
