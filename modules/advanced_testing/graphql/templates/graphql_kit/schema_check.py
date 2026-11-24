# Template from myOpenSDET: https://myopensdet.github.io/
"""Check that the fields your app uses still exist in a GraphQL schema.

A backend change can remove or rename a field. The API still answers, but every
query that asks for that field now fails. This script asks the server for its
schema (introspection) and compares it with expected_fields.json.

    python schema_check.py                              # GRAPHQL_URL, or the practice API
    python schema_check.py https://your-app.example.test/graphql

Exit code 0 when every field is there, 1 when something is missing.
"""

import json
import os
import sys
from pathlib import Path

from gql import GraphQLClient

PRACTICE_API = "https://graphqlzero.almansi.me/api"
EXPECTED = Path(__file__).parent / "expected_fields.json"

INTROSPECTION = """
query Fields {
  __schema {
    types {
      name
      fields { name type { kind name ofType { kind name ofType { kind name } } } }
    }
  }
}
"""


def type_name(t: dict) -> str:
    """Write a field's type the way the schema does: String, String!, [Post], [Post!]!."""
    if t["kind"] == "NON_NULL":
        return type_name(t["ofType"]) + "!"
    if t["kind"] == "LIST":
        return "[" + type_name(t["ofType"]) + "]"
    return t["name"]


def schema_fields(introspection: dict) -> dict[str, dict[str, str]]:
    """{"Post": {"id": "ID", "title": "String", ...}, ...} from an introspection answer."""
    return {
        t["name"]: {f["name"]: type_name(f["type"]) for f in t["fields"]}
        for t in introspection["__schema"]["types"]
        if t["fields"] and not t["name"].startswith("__")
    }


def compare(expected: dict, actual: dict) -> list[str]:
    """One line per problem. An empty list means every expected field is there."""
    problems = []
    for type_, fields in expected.items():
        if type_ not in actual:
            problems.append(f"missing type {type_}")
            continue
        for field, wanted in fields.items():
            found = actual[type_].get(field)
            if found is None:
                problems.append(f"missing field {type_}.{field}")
            elif found != wanted:
                problems.append(f"changed {type_}.{field}: expected {wanted}, found {found}")
    return problems


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GRAPHQL_URL", PRACTICE_API)
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    answer = GraphQLClient(url).execute(INTROSPECTION)
    if answer.errors:
        print(f"Introspection is off or failed: {answer.errors[0].get('message')}")
        print("Ask the team for the schema file (schema.graphql) and compare with that.")
        return 1
    problems = compare(expected, schema_fields(answer.data))
    checked = sum(len(fields) for fields in expected.values())
    for line in problems:
        print(line)
    print(f"{checked} fields checked, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
