# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Check that a response has the right shape, and list every problem with its path."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

SCHEMAS = Path(__file__).parents[1] / "schemas"


def load_schema(name: str) -> dict:
    return json.loads((SCHEMAS / name).read_text(encoding="utf-8"))


def _registry() -> Registry:
    """All schemas in the folder, so one can point to another with "$ref": "booking.json"."""
    resources = [
        (path.name, Resource.from_contents(load_schema(path.name)))
        for path in SCHEMAS.glob("*.json")
    ]
    return Registry().with_resources(resources)


def schema_errors(data, schema: dict) -> list[str]:
    """Every way the data breaks the schema, as "path: problem", in a stable order."""
    validator = Draft202012Validator(
        schema, registry=_registry(), format_checker=Draft202012Validator.FORMAT_CHECKER
    )
    errors = []
    for error in validator.iter_errors(data):
        path = "$" + "".join(
            f"[{part}]" if isinstance(part, int) else f".{part}" for part in error.absolute_path
        )
        errors.append(f"{path}: {error.message}")
    return sorted(errors)


def assert_matches_schema(data, schema: dict) -> None:
    errors = schema_errors(data, schema)
    if errors:
        lines = "\n".join(f"- {error}" for error in errors)
        raise AssertionError(f"The response doesn't match the schema:\n{lines}")
