import streamlit as st
from services.order_service import load_csv, save_csv, ORDERS_FILE

def show_admin_orders():
    st.title("Manage Orders")
    
    orders_df = load_csv(ORDERS_FILE)
    if orders_df.empty:
        st.info("No orders found")
        return

    # Filter by status
    status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Shipped", "Delivered"])
    
    view_df = orders_df
    if status_filter != "All":
        view_df = orders_df[orders_df['status'] == status_filter]

    st.dataframe(view_df)
    
    st.subheader("Update Order Status")
    order_id = st.number_input("Order ID", min_value=1, step=1)
    new_status = st.selectbox("New Status", ["Pending", "Shipped", "Delivered"])
    
    if st.button("Update Status"):
        if order_id in orders_df['id'].values:
            idx = orders_df.index[orders_df['id'] == order_id]
            orders_df.at[idx[0], 'status'] = new_status
            save_csv(orders_df, ORDERS_FILE)
            st.success(f"Order #{order_id} updated to {new_status}")
            st.rerun()
        else:
            st.error("Order ID not found")
