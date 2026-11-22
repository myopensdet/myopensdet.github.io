# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Drivers: how the steps reach the shop. The steps never know which one they use.

    ApiDriver  talks to the shop's API with requests
    UiDriver   clicks through the shop's web page with Playwright

Both have the same methods, so one feature file and one set of steps test both.
"""

from drivers.api_driver import ApiDriver
from drivers.ui_driver import UiDriver

TARGETS = ("api", "ui")

__all__ = ["TARGETS", "ApiDriver", "UiDriver"]
