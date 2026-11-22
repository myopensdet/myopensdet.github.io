# Template from myOpenSDET: https://myopensdet.github.io/
"""Link automated tests to requirement IDs, and print which IDs have tests.

Save this as conftest.py in your tests folder (or paste it into the one you have).
Then mark each test with the IDs it checks:

    @pytest.mark.covers("REF-1", "REF-4")
    def test_a_sale_item_after_31_days_is_refused(): ...

Run with the list of IDs your story or spec has:

    pytest --requirements REF-1,REF-2,REF-3

At the end, pytest prints how many tests check each ID, and which IDs have none.
"""

import pytest

COVERS = pytest.StashKey[dict]()


def pytest_addoption(parser):
    parser.addoption(
        "--requirements",
        default="",
        help="Comma-separated requirement IDs to report on, for example REF-1,REF-2",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "covers(*ids): the requirement IDs this test checks")
    config.stash[COVERS] = {}


def pytest_collection_modifyitems(config, items):
    covers = config.stash[COVERS]
    for item in items:
        for marker in item.iter_markers(name="covers"):
            for requirement in marker.args:
                covers.setdefault(requirement, []).append(item.nodeid)


def pytest_terminal_summary(terminalreporter, config):
    covers = config.stash[COVERS]
    wanted = [r.strip() for r in config.getoption("requirements").split(",") if r.strip()]
    if not wanted and not covers:
        return
    terminalreporter.section("requirements")
    for requirement in wanted or sorted(covers):
        count = len(covers.get(requirement, []))
        status = f"{count} test{'s' if count != 1 else ''}" if count else "NO TESTS"
        terminalreporter.write_line(f"{requirement:<10} {status}")
    unknown = sorted(set(covers) - set(wanted)) if wanted else []
    for requirement in unknown:
        terminalreporter.write_line(f"{requirement:<10} not in --requirements (typo?)")
