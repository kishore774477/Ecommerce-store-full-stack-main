import streamlit as st
from services.order_service import load_csv, ORDERS_FILE

def show_order_history():
    st.title("My Orders")
    
    if 'user' not in st.session_state:
        st.warning("Please sign in to view orders")
        return

    orders_df = load_csv(ORDERS_FILE)
    if orders_df.empty:
        st.info("No orders found")
        return

    user_id = st.session_state['user']['id']
    user_orders = orders_df[orders_df['user_id'] == user_id]
    
    if user_orders.empty:
        st.info("You haven't placed any orders yet.")
        return

    for index, row in user_orders.iterrows():
        with st.expander(f"Order #{row['id']} - {row['created_at'][:10]} - ${row['total_amount']:.2f}"):
            st.write(f"Status: {row['status']}")
            st.write(f"Items: {row['items']}")
