# Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/
"""Make test_data/discount_rules.xlsx: the sheet the business team keeps their discount rules in.

At work you get this file from them. This script only exists so the sample is easy to rebuild:
    python tools/make_discount_sheet.py
"""

from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

CREDIT = "Template from myOpenSDET: https://arshaduzzaman-sm.github.io/myopensdet/"
ROWS = [
    ("rule", "subtotal", "coupon", "member", "expected_total"),
    ("Plain order", 45.5, None, False, 45.5),
    ("Ten percent off", 19.99, "SAVE10", False, 17.99),
    ("Member price", 19.99, None, True, 18.99),
    ("Ten percent off for a member", 100, "SAVE10", True, 85.5),
    ("Welcome coupon", 25, "WELCOME5", False, 20),
    ("Welcome coupon too small", 15, "WELCOME5", False, 15),
]


def main() -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Discounts"
    for row in ROWS:
        sheet.append(row)
    workbook.properties.creator = "myOpenSDET"
    workbook.properties.description = CREDIT
    workbook.properties.created = workbook.properties.modified = datetime(2026, 11, 1)
    path = Path(__file__).resolve().parents[1] / "test_data" / "discount_rules.xlsx"
    workbook.save(path)
    print(f"Saved {path.name}")


if __name__ == "__main__":
    main()
