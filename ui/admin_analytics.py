import plotly.express as px
import streamlit as st

from models.analytics import AnalyticsEngine
from models.recommender import RecommenderSystem
from services.order_service import OrderService
from services.product_service import ProductService
from ui.components import require_admin
from utils.helpers import format_price


def show_admin_analytics():
    st.title("Business Analytics")
    if not require_admin():
        return

    orders_df = OrderService().get_all_orders()
    products_df = ProductService().get_all_products()
    analytics = AnalyticsEngine(orders_df, products_df)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", format_price(analytics.get_total_sales()))
    c2.metric("Total Orders", analytics.get_orders_count())
    c3.metric("Avg Order Value", format_price(analytics.get_average_order_value()))

    if orders_df.empty:
        st.info("No orders yet — analytics will appear once customers start buying.")
        return

    st.subheader("Sales Trend")
    sales = analytics.get_sales_over_time()
    if not sales.empty:
        st.plotly_chart(px.area(sales, x="date", y="revenue", title="Revenue over Time"), width="stretch")

    left, right = st.columns(2)
    with left:
        st.subheader("Order Status Distribution")
        status = analytics.get_status_counts()
        st.plotly_chart(px.pie(status, values="orders", names="status", hole=0.4), width="stretch")
    with right:
        st.subheader("Revenue by Category")
        by_cat = analytics.get_sales_by_category()
        if not by_cat.empty:
            st.plotly_chart(px.bar(by_cat, x="category", y="revenue"), width="stretch")

    st.subheader("Top Selling Products")
    top = analytics.get_top_products(10)
    st.dataframe(top, hide_index=True, width="stretch",
                 column_config={"revenue": st.column_config.NumberColumn(format="$%.2f")})

    pairs = RecommenderSystem(products_df, orders_df).frequently_bought_pairs()
    if pairs:
        st.subheader("Frequently Bought Together")
        names = dict(zip(products_df["id"], products_df["name"]))
        for (a, b), n in pairs:
            st.markdown(f"- **{names.get(a, a)}** + **{names.get(b, b)}** — {n} order(s)")
