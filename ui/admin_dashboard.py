import plotly.express as px
import streamlit as st

from models.analytics import AnalyticsEngine
from services.auth_service import AuthService
from services.inventory_service import InventoryService
from services.order_service import OrderService
from services.product_service import ProductService
from ui.components import require_admin
from utils.helpers import format_price


def show_admin_dashboard():
    st.title("Admin Dashboard")
    if not require_admin():
        return

    orders_df = OrderService().get_all_orders()
    products_df = ProductService().get_all_products()
    analytics = AnalyticsEngine(orders_df, products_df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Sales", format_price(analytics.get_total_sales()))
    c2.metric("Orders", analytics.get_orders_count())
    c3.metric("Products", len(products_df))
    c4.metric("Customers", int((AuthService().get_all_users()["role"] == "customer").sum()))

    left, right = st.columns([3, 2])
    with left:
        st.subheader("Sales over time")
        sales = analytics.get_sales_over_time()
        if not sales.empty:
            fig = px.line(sales, x="date", y="revenue", markers=True)
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No sales data available yet")

    with right:
        st.subheader("⚠️ Low stock")
        low = InventoryService().get_low_stock()
        if low.empty:
            st.success("All products are well stocked")
        else:
            st.dataframe(low, hide_index=True, width="stretch")

    st.subheader("Recent orders")
    if orders_df.empty:
        st.info("No orders yet")
    else:
        recent = orders_df.sort_values("created_at", ascending=False).head(10)
        st.dataframe(recent[["id", "user_id", "total_amount", "status", "created_at"]],
                     hide_index=True, width="stretch")
