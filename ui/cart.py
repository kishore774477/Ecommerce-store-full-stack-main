import streamlit as st

from services.cart_service import CartService
from services.product_service import ProductService
from ui.components import PLACEHOLDER_IMAGE, go_to
from utils.helpers import format_price


def show_cart():
    st.title("Shopping Cart")

    cart = st.session_state.setdefault("cart", {})
    cart_service = CartService()
    items = cart_service.get_cart_items(cart, ProductService())

    # Drop products that were removed from the catalogue
    valid_ids = {i["id"] for i in items}
    for pid in [p for p in cart if p not in valid_ids]:
        cart.pop(pid)

    if not items:
        st.info("Your cart is empty")
        if st.button("Go Shopping", type="primary"):
            go_to("home")
        return

    for item in items:
        with st.container(border=True):
            c1, c2, c3, c4, c5 = st.columns([1, 3, 2, 2, 1], vertical_alignment="center")
            c1.image(item["image"] or PLACEHOLDER_IMAGE, width=80)
            c2.markdown(f"**{item['name']}**  \n{format_price(item['price'])} each")
            new_qty = c3.number_input(
                "Qty", min_value=1, max_value=max(item["stock"], item["quantity"]),
                value=item["quantity"], step=1, key=f"qty_{item['id']}",
            )
            if new_qty != item["quantity"]:
                cart_service.update_quantity(cart, item["id"], new_qty)
                st.rerun()
            c4.markdown(f"**{format_price(item['subtotal'])}**")
            if c5.button("🗑️", key=f"del_{item['id']}", help="Remove"):
                cart_service.remove_from_cart(cart, item["id"])
                st.rerun()
            if item["quantity"] > item["stock"]:
                st.warning(f"Only {item['stock']} in stock — please reduce the quantity.")

    total = sum(i["subtotal"] for i in items)
    st.divider()
    c1, c2, c3 = st.columns([2, 1, 1])
    c1.subheader(f"Total: {format_price(total)}")
    if c2.button("Clear cart"):
        cart.clear()
        st.rerun()
    if c3.button("Proceed to Checkout", type="primary"):
        go_to("checkout")
