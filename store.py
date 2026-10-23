
from pyscript import document
from pyodide.ffi import create_proxy

# Casetique product list
products = {
    "1": {"name": "Blush Glitter", "price": 18.00},
    "2": {"name": "Sunflower Bloom", "price": 20.00},
    "3": {"name": "Patchwork Pastel", "price": 16.00},
    "4": {"name": "Midnight Memory", "price": 22.00},
}

def setup_dropdowns():
    # Case dropdown
    product_select = document.getElementById("f-product")
    product_select.innerHTML = (
        '<option value="">Select a case</option>'
    )

    for product_id, product in products.items():
        option = document.createElement("option")
        option.value = product_id
        option.textContent = product["name"]
        product_select.appendChild(option)

    # Phone model dropdown
    model_select = document.getElementById("f-model")
    model_select.innerHTML = (
        '<option value="">Select your phone model</option>'
        '<option value="Android">Android</option>'
        '<option value="iOS">iOS</option>'
    )

def update_total(event=None):
    product_id = document.getElementById("f-product").value
    qty_value = document.getElementById("f-qty").value

    try:
        quantity = int(qty_value)
    except (ValueError, TypeError):
        quantity = 1

    quantity = max(1, min(quantity, 10))

    if product_id in products:
        total = products[product_id]["price"] * quantity
    else:
        total = 0.00

    document.getElementById("total").textContent = (
        f"${total:.2f}"
    )

def place_order(event):
    event.preventDefault()

    product_id = document.getElementById("f-product").value
    model = document.getElementById("f-model").value
    qty_value = document.getElementById("f-qty").value
    name = document.getElementById("f-name").value.strip()
    email = document.getElementById("f-email").value.strip()
    message = document.getElementById("order-msg")

    # Validate required fields
    if not product_id or product_id not in products:
        message.textContent = "Please select a case."
        return

    if model not in ("Android", "iOS"):
        message.textContent = "Please select Android or iOS."
        return

    try:
        quantity = int(qty_value)
    except (ValueError, TypeError):
        message.textContent = "Please enter a valid quantity."
        return

    if quantity < 1 or quantity > 10:
        message.textContent = "Quantity must be between 1 and 10."
        return

    if not name:
        message.textContent = "Please enter your name."
        return

    if not email or "@" not in email or "." not in email.split("@")[-1]:
        message.textContent = "Please enter a valid email address."
        return

    # Calculate order total
    product = products[product_id]
    total = product["price"] * quantity

    # Display confirmation
    message.textContent = (
        f"Thank you for your order, {name}! "
        f"Case: {product['name']} | "
        f"Phone: {model} | "
        f"Quantity: {quantity} | "
        f"Total: ${total:.2f}. "
        "Your order details have been confirmed on this page."
    )

    # Update total display
    document.getElementById("total").textContent = f"${total:.2f}"

def subscribe(event):
    event.preventDefault()

    email = document.getElementById("news-email").value.strip()
    message = document.getElementById("news-msg")

    if not email or "@" not in email or "." not in email.split("@")[-1]:
        message.textContent = "Please enter a valid email address."
        return

    message.textContent = "Thank you for subscribing to Casetique!"

# Initialize the website
setup_dropdowns()
update_total()

# Register event listeners
document.getElementById("f-product").addEventListener(
    "change", create_proxy(update_total)
)
document.getElementById("f-qty").addEventListener(
    "input", create_proxy(update_total)
)
document.getElementById("order-form").addEventListener(
    "submit", create_proxy(place_order)
)
document.getElementById("news-form").addEventListener(
    "submit", create_proxy(subscribe)
)
