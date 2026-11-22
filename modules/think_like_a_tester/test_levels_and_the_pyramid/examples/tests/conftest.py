# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Mark every test with its level, from the folder it lives in.

Put this file in your tests/ folder. Then sort tests into folders:

    tests/unit/  tests/integration/  tests/api/  tests/ui/  tests/e2e/

and run one level at a time:

    pytest -m unit              the fast ones, on every save
    pytest -m "not ui"          everything except the browser tests
    pytest -m "api or e2e"      before a release

Nobody has to remember to add @pytest.mark.unit by hand.
"""

import pytest

LEVELS = ("unit", "integration", "api", "ui", "e2e")


def pytest_collection_modifyitems(config, items):
    for item in items:
        folders = item.path.relative_to(config.rootpath).parts[:-1]
        for level in LEVELS:
            if level in folders:
                item.add_marker(getattr(pytest.mark, level))
