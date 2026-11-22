# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Every template has a test that proves it works."""

import importlib.util
from pathlib import Path

# Load the template by its path, so this test works wherever the folder is copied.
TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "example_template.py"
spec = importlib.util.spec_from_file_location("example_template", TEMPLATE)
example_template = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example_template)


def test_greeting_uses_the_name():
    assert example_template.build_greeting("Arshad") == "Hello, Arshad!"


def test_greeting_ignores_extra_spaces():
    assert example_template.build_greeting("  Arshad  ") == "Hello, Arshad!"
