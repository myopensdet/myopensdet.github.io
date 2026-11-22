# Template from myOpenSDET: https://myopensdet.github.io/
"""Lesson: strings, lists and dictionaries. Run: python collections_demo.py"""

message = "  Refunds are possible up to 30 days after delivery  "
print(message.strip())
print("30 days" in message, message.lower().count("d"))
print(message.strip().split(" ")[:3])

users = ["arshad", "maria", "admin"]
users.append("আরশাদ")
print(len(users), users[0], users[-1], users[1:3])

product = {"id": 7, "name": "Pocket notebook", "price": 4.25}
print(product["name"], product.get("colour"), product.get("colour", "none"))
product["in_stock"] = True
print(list(product.keys()))
