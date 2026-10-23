"""Casetique page logic in Python (PyScript). Backend rules live in store.py."""
from html import escape

from pyscript import document, when

import store

state = {"selected": store.PRODUCTS[0]["id"], "filter": None}


def q(selector):
    return document.querySelector(selector)


def money(value):
    return f"${value:.2f}"


def asset(path):
    return f"static/{path}"


def update_total():
    qty_el = q("#f-qty")
    q("#total").textContent = money(store.line_total(q("#f-product").value, qty_el.value))


def select(product_id):
    product = store.get_product(product_id)
    if product is None:
        return
    state["selected"] = product_id
    q("#phone-img").src = asset(product["image"])
    q("#phone-img").alt = f"{product['name']} phone case"
    q("#phone-label").textContent = product["name"]
    q("#f-product").value = str(product_id)
    for card in document.querySelectorAll(".card"):
        card.classList.toggle("is-selected", int(card.dataset.id) == product_id)
    update_total()


def render_filters():
    items = [("all", "All cases")] + [(str(p["id"]), p["name"]) for p in store.PRODUCTS]
    active = "all" if state["filter"] is None else str(state["filter"])
    q("#filters").innerHTML = "".join(
        f'<button type="button" class="chip{" is-active" if key == active else ""}" '
        f'data-id="{key}" aria-pressed="{str(key == active).lower()}">{escape(label)}</button>'
        for key, label in items
    )


def render_grid():
    cards = []
    for p in store.PRODUCTS:
        if state["filter"] is not None and p["id"] != state["filter"]:
            continue
        selected = " is-selected" if p["id"] == state["selected"] else ""
        badge = f'<span class="badge">{escape(p["tag"])}</span>' if p["tag"] else ""
        cards.append(
            f'<button type="button" class="card{selected}" data-id="{p["id"]}">'
            f'{badge}'
            f'<div class="swatch" style="background:{escape(p["color"])}40">'
            f'<img src="{asset(p["image"])}" alt="{escape(p["name"])} phone case" loading="lazy"></div>'
            f'<h3>{escape(p["name"])}</h3>'
            f'<p class="meta">{escape(p["blurb"])}</p>'
            f'<span class="price">{money(p["price"])}</span></button>'
        )
    q("#grid").innerHTML = "".join(cards)


def show(selector, text, ok):
    el = q(selector)
    el.textContent = text
    el.className = "msg " + ("ok" if ok else "error")


@when("click", "#filters")
def on_filter(event):
    button = event.target.closest("button[data-id]")
    if button is None:
        return
    key = button.dataset.id
    state["filter"] = None if key == "all" else int(key)
    render_filters()
    render_grid()
    if state["filter"] is not None:
        select(state["filter"])


@when("click", "#grid")
def on_card(event):
    card = event.target.closest(".card")
    if card is not None:
        select(int(card.dataset.id))


@when("change", "#f-product")
def on_product_change(event):
    select(int(q("#f-product").value))


@when("input", "#f-qty")
def on_qty(event):
    update_total()


@when("submit", "#order-form")
def on_order(event):
    event.preventDefault()
    ok, message = store.create_order(
        q("#f-name").value, q("#f-email").value, q("#f-model").value,
        q("#f-product").value, q("#f-qty").value,
    )
    show("#order-msg", message, ok)
    if ok:
        q("#order-form").reset()
        select(state["selected"])


@when("submit", "#news-form")
def on_subscribe(event):
    event.preventDefault()
    ok, message = store.subscribe(q("#news-email").value)
    show("#news-msg", message, ok)
    if ok:
        q("#news-form").reset()


q("#f-product").innerHTML = "".join(
    f'<option value="{p["id"]}">{escape(p["name"])} ({money(p["price"])})</option>'
    for p in store.PRODUCTS
)
q("#f-model").innerHTML = '<option value="">Choose your phone</option>' + "".join(
    f"<option>{escape(m)}</option>" for m in store.MODELS
)
render_filters()
render_grid()
select(state["selected"])
