# Template from myOpenSDET: https://myopensdet.github.io/
"""Which spec, which API, which values. Point it at your own API with environment variables:

    OPENAPI_SPEC=https://staging.example.com/openapi.json \
    BASE_URL=https://staging.example.com/api \
    AUTH_HEADER=Authorization AUTH_VALUE="Bearer $API_TOKEN" python -m pytest
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # to import openapi_check

SPEC = os.environ.get("OPENAPI_SPEC", "https://petstore3.swagger.io/api/v3/openapi.json")
BASE_URL = os.environ.get("BASE_URL", "https://petstore3.swagger.io/api/v3").rstrip("/")

# Values for path and query parameters the spec has no example for. Use test data that
# exists on your test environment.
PARAMS = {"petId": "1", "orderId": "1", "username": "user1", "tags": "tag1"}

# A login header, if you have one. The value comes only from the environment.
AUTH_HEADER = os.environ.get("AUTH_HEADER")
AUTH_VALUE = os.environ.get("AUTH_VALUE")
HEADERS = {AUTH_HEADER: AUTH_VALUE} if AUTH_HEADER and AUTH_VALUE else {}
