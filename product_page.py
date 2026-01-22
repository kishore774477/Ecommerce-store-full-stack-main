import streamlit as st
from services.product_service import ProductService
from services.cart_service import CartService

def show_product_page():
    if 'selected_product' not in st.session_state:
        st.error("No product selected")
        if st.button("Back to Home"):
            st.session_state['page'] = 'home'
            st.rerun()
        return

    product_id = st.session_state['selected_product']
    product_service = ProductService()
    product = product_service.get_product_by_id(product_id)
    
    if not product:
        st.error("Product not found")
        return

    if st.button("← Back"):
        st.session_state['page'] = 'home'
        st.rerun()

    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.image(product['image'])
        
    with c2:
        st.title(product['name'])
        st.subheader(f"${product['price']}")
        st.write(product['description'])
        st.write(f"Category: {product['category']}")
        
        if st.button("Add to Cart"):
            cart_service = CartService()
            if 'cart' not in st.session_state:
                st.session_state['cart'] = {}
            
            st.session_state['cart'] = cart_service.add_to_cart(st.session_state['cart'], product['id'])
            st.success(f"Added {product['name']} to cart!")
