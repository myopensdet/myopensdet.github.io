# Template from myOpenSDET: https://myopensdet.github.io/
from ex06_classes import TestRun


def make_run():
    run = TestRun("nightly")
    run.add("test_login", "passed")
    run.add("test_device_list", "failed")
    run.add("test_export", "skipped")
    run.add("test_battery_alert", "failed")
    return run


def test_new_run_is_empty():
    run = TestRun("smoke")
    assert run.name == "smoke"
    assert run.count("passed") == 0
    assert run.failed_tests() == []


def test_count_each_outcome():
    run = make_run()
    assert run.count("passed") == 1
    assert run.count("failed") == 2
    assert run.count("skipped") == 1


def test_failed_tests_keep_their_order():
    assert make_run().failed_tests() == ["test_device_list", "test_battery_alert"]


def test_summary():
    assert make_run().summary() == "nightly: 4 tests, 2 failed"


def test_two_runs_are_separate():
    first, second = TestRun("first"), TestRun("second")
    first.add("test_login", "failed")
    assert second.count("failed") == 0
