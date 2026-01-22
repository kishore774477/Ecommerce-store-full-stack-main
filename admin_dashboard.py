import streamlit as st
from models.analytics import AnalyticsEngine
from services.product_service import ProductService
from services.order_service import OrderService
from utils.helpers import load_csv
from config.settings import RAW_DATA_DIR
import os
import plotly.express as px

def show_admin_dashboard():
    st.title("Admin Dashboard")
    
    # Simple check for admin (username == 'admin' for demo)
    if 'user' not in st.session_state or st.session_state['user'].get('username') != 'admin':
        st.error("Access Denied")
        return

    orders_file = os.path.join(RAW_DATA_DIR, 'orders.csv')
    orders_df = load_csv(orders_file) 
    
    analytics = AnalyticsEngine(orders_df)
    
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Total Sales", f"${analytics.get_total_sales():.2f}")
    with c2:
        st.metric("Total Orders", analytics.get_orders_count())
        
    st.subheader("Sales Over Time")
    sales_data = analytics.get_sales_over_time()
    if not sales_data.empty:
        fig = px.line(sales_data, title='Sales Trend')
        st.plotly_chart(fig)
    else:
        st.info("No sales data available")
