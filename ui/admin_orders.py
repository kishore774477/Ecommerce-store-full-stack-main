import streamlit as st

from config.settings import ORDER_STATUSES
from services.order_service import OrderService
from ui.components import require_admin


def show_admin_orders():
    st.title("Manage Orders")
    if not require_admin():
        return

    order_service = OrderService()
    orders_df = order_service.get_all_orders()
    if orders_df.empty:
        st.info("No orders found")
        return

    status_filter = st.selectbox("Filter by Status", ["All"] + ORDER_STATUSES)
    view_df = orders_df if status_filter == "All" else orders_df[orders_df["status"] == status_filter]
    view_df = view_df.sort_values("created_at", ascending=False)
    st.dataframe(view_df.drop(columns=["items"]), hide_index=True, width="stretch")

    st.subheader("Update Order Status")
    c1, c2, c3 = st.columns([2, 2, 1], vertical_alignment="bottom")
    order_id = c1.selectbox("Order", orders_df["id"].sort_values(ascending=False).tolist(),
                            format_func=lambda i: f"Order #{i}")
    current = orders_df.loc[orders_df["id"] == order_id, "status"].iloc[0]
    new_status = c2.selectbox("New Status", ORDER_STATUSES, index=ORDER_STATUSES.index(current)
                              if current in ORDER_STATUSES else 0)
    if c3.button("Update", type="primary"):
        ok, msg = order_service.update_status(order_id, new_status)
        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)

    with st.expander(f"Items in order #{order_id}"):
        row = orders_df[orders_df["id"] == order_id].iloc[0]
        for line in order_service.describe_items(row["items"]):
            st.markdown(f"- {line['quantity']} × {line['name']}")
        st.caption(f"Ship to: {row['address']}")
