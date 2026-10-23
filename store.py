"""Casetique "backend" running in the browser with PyScript.

Holds the catalog, validates orders and signups, and saves them in the
visitor's browser (localStorage). No server is involved.
"""
import json
import re

try:                                   # inside the browser (Pyodide)
    from js import localStorage
except ImportError:                    # plain Python, e.g. for testing
    class _MemoryStorage(dict):
        def getItem(self, key):
            return self.get(key)

        def setItem(self, key, value):
            self[key] = value

    localStorage = _MemoryStorage()

PRODUCTS = [
    {"id": 1, "name": "Pinkish clear", "image": "img/clear.png", "style": "Clear", "price": 19,
     "color": "#E3C9C4", "tag": "Best seller",
     "blurb": "Shimmering blush shell with a built-in MagSafe ring and metal camera frame."},
    {"id": 2, "name": "Sunflower Bloom", "image": "img/floral.png", "style": "Floral", "price": 20.0,
     "color": "#F0C98B", "tag": "New",
     "blurb": "Bold hand-painted blooms on a clear back with a black bumper edge."},
    {"id": 3, "name": "Girly pattern", "image": "img/pattern.png", "style": "Pattern", "price": 16.0,
     "color": "#B7C4A6", "tag": "",
     "blurb": "Gingham, ditsy florals and little bows in soft pastel patches."},
    {"id": 4, "name": "Solid customize", "image": "img/solid.png", "style": "Solid", "price": 22.0,
     "color": "#7E9471", "tag": "Custom photo",
     "blurb": "Clear shock-absorbing bumpers around a dark back made for your own photo."},
]

MODELS = ["iPhone 15", "iPhone 15 Pro", "iPhone 16", "Galaxy S24", "Galaxy S25", "Pixel 9"]
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ORDERS_KEY = "casetique_orders"
SUBS_KEY = "casetique_subscribers"


def _load(key):
    try:
        return json.loads(localStorage.getItem(key) or "[]")
    except (ValueError, TypeError):
        return []


def _save(key, rows):
    try:
        localStorage.setItem(key, json.dumps(rows))
        return True
    except Exception:                  # storage blocked or full
        return False


def get_product(product_id):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)


def line_total(product_id, quantity):
    try:
        product = get_product(int(product_id))
    except (TypeError, ValueError):
        product = None
    try:
        qty = max(1, min(10, int(quantity)))
    except (TypeError, ValueError):
        qty = 1
    return round(product["price"] * qty, 2) if product else 0.0


def create_order(name, email, model, product_id, quantity):
    """Return (ok, message)."""
    name, email = str(name).strip(), str(email).strip()
    try:
        product_id, quantity = int(product_id), int(quantity)
    except (TypeError, ValueError):
        return False, "Choose a case and a quantity."
    product = get_product(product_id)
    if not name:
        return False, "Enter your name."
    if not EMAIL_RE.match(email):
        return False, "Enter a valid email address."
    if model not in MODELS:
        return False, "Choose your phone model."
    if product is None:
        return False, "That case is no longer available."
    if not 1 <= quantity <= 10:
        return False, "Quantity must be between 1 and 10."

    orders = _load(ORDERS_KEY)
    orders.append({
        "id": len(orders) + 1, "name": name, "email": email, "model": model,
        "product_id": product_id, "quantity": quantity,
        "total": round(product["price"] * quantity, 2),
    })
    if not _save(ORDERS_KEY, orders):
        return False, "Couldn't save your order in this browser. Check your privacy settings."
    return True, f"Order #{len(orders)} placed. Total ${orders[-1]['total']:.2f}."


def subscribe(email):
    """Return (ok, message)."""
    email = str(email).strip().lower()
    if not EMAIL_RE.match(email):
        return False, "Enter a valid email address."
    subs = _load(SUBS_KEY)
    if email in subs:
        return True, "You're already on the list."
    subs.append(email)
    if not _save(SUBS_KEY, subs):
        return False, "Couldn't save your signup in this browser."
    return True, "You're on the list."
