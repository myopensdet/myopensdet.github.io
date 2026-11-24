# Template from myOpenSDET: https://myopensdet.github.io/
import json

from schema_check import EXPECTED, INTROSPECTION, compare, schema_fields


def test_every_field_the_app_uses_is_still_there(client):
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    actual = schema_fields(client.data(INTROSPECTION))
    assert compare(expected, actual) == []
