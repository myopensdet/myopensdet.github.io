# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""The same calls through ApiClient, with logging and a clear failure. Run: python client_demo.py"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "templates" / "booker_api_tests"))
from api.client import ApiClient, check_status  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(name)s: %(message)s")

with ApiClient("https://restful-booker.herokuapp.com", timeout=15) as api:
    check_status(api.get("/ping"), 201)
    check_status(api.get("/booking", params={"firstname": "Test"}), 200)
    try:
        check_status(
            api.put("/booking/1", json={}, headers={"Cookie": "token=not-a-real-token"}), 200
        )
    except AssertionError as failure:
        print(failure)
