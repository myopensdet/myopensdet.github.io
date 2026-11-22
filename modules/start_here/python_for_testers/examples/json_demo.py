# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: JSON. Run: python json_demo.py"""

import json

body = '{"id": 7, "name": "Pocket notebook", "price": 4.25, "tags": ["paper"], "sale": null}'
product = json.loads(body)  # JSON text -> Python dict
print(type(product), product["price"], product["sale"], product["tags"][0])

order = {"customer": "আরশাদ", "items": 2, "paid": True}
print(json.dumps(order))
print(json.dumps(order, ensure_ascii=False))
print(json.dumps(order, indent=2, ensure_ascii=False))
