import streamlit as st

from services.cart_service import CartService
from services.inventory_service import InventoryService
from services.order_service import OrderService
from services.payment_service import PaymentService
from services.product_service import ProductService
from ui.components import flash, go_to, require_login
from utils.helpers import format_price


def show_checkout():
    st.title("Checkout")

    if not require_login("Please sign in to checkout"):
        return

    cart = st.session_state.get("cart", {})
    if not cart:
        st.error("Cart is empty")
        if st.button("Go Shopping"):
            go_to("home")
        return

    cart_service = CartService()
    items = cart_service.get_cart_items(cart, ProductService())
    total = sum(i["subtotal"] for i in items)

    ok, msg = InventoryService().check_availability(cart)
    if not ok:
        st.error(f"{msg}. Please update your cart.")
        if st.button("Back to cart"):
            go_to("cart")
        return

    left, right = st.columns([3, 2])
    with right:
        with st.container(border=True):
            st.subheader("Order summary")
            for i in items:
                st.markdown(f"{i['quantity']} × {i['name']} — {format_price(i['subtotal'])}")
            st.divider()
            st.markdown(f"### Total: {format_price(total)}")

    with left:
        payment_method = st.radio("Payment method", ["Card", "Cash on Delivery"], horizontal=True)
        with st.form("checkout_form"):
            st.subheader("Shipping information")
            full_name = st.text_input("Full name")
            address = st.text_area("Delivery address")
            phone = st.text_input("Phone number")

            card_number = expiry = cvv = ""
            if payment_method == "Card":
                st.subheader("Card details")
                st.caption("Demo payment — no real charge. Test card: 4242 4242 4242 4242")
                card_number = st.text_input("Card number", max_chars=23)
                c1, c2 = st.columns(2)
                expiry = c1.text_input("Expiry (MM/YY)", max_chars=5)
                cvv = c2.text_input("CVV", type="password", max_chars=4)

            submitted = st.form_submit_button(f"Place order · {format_price(total)}", type="primary")

        if submitted:
            if not full_name.strip() or not address.strip() or not phone.strip():
                st.error("Please fill in your name, address and phone number.")
                return
            paid, pay_msg, ref = PaymentService().process_payment(
                total, card_number, expiry, cvv, method=payment_method)
            if not paid:
                st.error(pay_msg)
                return

            full_address = f"{full_name.strip()}, {address.strip()}, Ph: {phone.strip()}"
            user_id = st.session_state["user"]["id"]
            success, order_msg, order_id = OrderService().create_order(
                user_id, cart, full_address, payment_method, ref)
            if success:
                st.session_state["cart"] = {}
                st.session_state["last_order_id"] = order_id
                flash(f"🎉 {order_msg}. {pay_msg}.")
                st.session_state["celebrate"] = True
                go_to("order_history")
            else:
                st.error(order_msg)
