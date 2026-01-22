import streamlit as st
from models.analytics import AnalyticsEngine
from services.order_service import load_csv, ORDERS_FILE
import plotly.express as px

def show_admin_analytics():
    st.title("Business Analytics")
    
    orders_df = load_csv(ORDERS_FILE)
    analytics = AnalyticsEngine(orders_df)
    
    # Key Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"${analytics.get_total_sales():.2f}")
    c2.metric("Total Orders", analytics.get_orders_count())
    c3.metric("Avg Order Value", f"${analytics.get_total_sales() / max(analytics.get_orders_count(), 1):.2f}")
    
    # Charts
    st.subheader("Sales Trend")
    sales_data = analytics.get_sales_over_time()
    if not sales_data.empty:
        fig = px.area(sales_data, title='Revenue over Time')
        st.plotly_chart(fig, use_container_width=True)
        
    st.subheader("Order Status Distribution")
    if not orders_df.empty:
        status_counts = orders_df['status'].value_counts()
        fig2 = px.pie(values=status_counts.values, names=status_counts.index, title='Orders by Status')
        st.plotly_chart(fig2)
