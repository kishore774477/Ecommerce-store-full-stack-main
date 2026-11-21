import streamlit as st

from services.order_service import OrderService
from ui.components import require_login, show_flash
from utils.helpers import format_price

STATUS_ICON = {"Pending": "🕒", "Shipped": "🚚", "Delivered": "✅", "Cancelled": "❌"}


def show_order_history():
    show_flash()
    if st.session_state.pop("celebrate", False):
        st.balloons()
    st.title("My Orders")

    if not require_login("Please sign in to view orders"):
        return

    order_service = OrderService()
    user_orders = order_service.get_orders_for_user(st.session_state["user"]["id"])
    if user_orders.empty:
        st.info("You haven't placed any orders yet.")
        return

    last_id = st.session_state.get("last_order_id")
    for _, row in user_orders.iterrows():
        icon = STATUS_ICON.get(row["status"], "")
        label = (f"Order #{row['id']} · {str(row['created_at'])[:10]} · "
                 f"{format_price(row['total_amount'])} · {icon} {row['status']}")
        with st.expander(label, expanded=(row["id"] == last_id)):
            for line in order_service.describe_items(row["items"]):
                st.markdown(f"- {line['quantity']} × {line['name']}")
            if row["address"]:
                st.caption(f"Ship to: {row['address']}")
            if row["payment_method"]:
                st.caption(f"Payment: {row['payment_method']} ({row['payment_ref']})")
            if row["status"] == "Pending":
                if st.button("Cancel order", key=f"cancel_{row['id']}"):
                    ok, msg = order_service.cancel_order(row["id"], st.session_state["user"]["id"])
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.rerun()
