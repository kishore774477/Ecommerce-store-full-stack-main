import streamlit as st
from services.order_service import OrderService
from services.cart_service import CartService
from services.product_service import ProductService

def show_checkout():
    st.title("Checkout")
    
    if 'user' not in st.session_state:
        st.warning("Please sign in to checkout")
        st.session_state['page'] = 'login'
        st.rerun()
        return

    if 'cart' not in st.session_state or not st.session_state['cart']:
        st.error("Cart is empty")
        return
        
    cart_service = CartService()
    product_service = ProductService()
    total = cart_service.get_cart_total(st.session_state['cart'], product_service)
    
    st.subheader(f"Total Amount: ${total:.2f}")
    
    st.write("Shipping Information")
    address = st.text_area("Delivery Address")
    
    if st.button("Place Order"):
        if not address:
            st.error("Please provide an address")
            return
            
        order_service = OrderService()
        user_id = st.session_state['user']['id']
        success, msg = order_service.create_order(user_id, st.session_state['cart'], total)
        
        if success:
            st.success(msg)
            st.balloons()
            st.session_state['cart'] = {}
            st.session_state['page'] = 'home'
        else:
            st.error(msg)
