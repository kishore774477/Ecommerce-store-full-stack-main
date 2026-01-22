import streamlit as st
from services.product_service import ProductService

def show_home():
    st.title("Welcome to Our Store")
    
    product_service = ProductService()
    products = product_service.get_all_products()
    
    if products.empty:
        st.info("No products available.")
        return

    cols = st.columns(3)
    for index, row in products.iterrows():
        with cols[index % 3]:
            st.image(row['image'], width=150)
            st.subheader(row['name'])
            st.write(f"${row['price']}")
            if st.button(f"View Details {row['name']}", key=f"btn_{row['id']}"):
                st.session_state['selected_product'] = row['id']
                st.session_state['page'] = 'product_page'
                st.rerun()
