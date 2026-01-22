import streamlit as st
from services.inventory_service import InventoryService
from services.product_service import ProductService

def show_admin_inventory():
    st.title("Inventory Management")
    
    product_service = ProductService()
    inventory_service = InventoryService()
    
    products = product_service.get_all_products()
    
    if products.empty:
        st.info("No products found")
        return

    # Enrich with stock info
    # We do a fresh check or just iterate
    
    data = []
    for index, row in products.iterrows():
         stock = inventory_service.get_stock(row['id'])
         data.append({
             "ID": row['id'],
             "Name": row['name'],
             "Current Stock": stock
         })
         
    st.dataframe(data)

    st.subheader("Update Stock")
    c1, c2 = st.columns(2)
    with c1:
        selected_id = st.selectbox("Select Product", products['id'])
    with c2:
        qty_change = st.number_input("Add/Remove Quantity", step=1, value=0)
        
    if st.button("Update Stock"):
        success, msg = inventory_service.update_stock(selected_id, qty_change)
        if success:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)
