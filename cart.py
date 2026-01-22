import streamlit as st
from services.cart_service import CartService
from services.product_service import ProductService

def show_cart():
    st.title("Shopping Cart")
    
    if 'cart' not in st.session_state or not st.session_state['cart']:
        st.info("Your cart is empty")
        if st.button("Go Shopping"):
            st.session_state['page'] = 'home'
            st.rerun()
        return

    cart_service = CartService()
    product_service = ProductService()
    products = product_service.get_all_products()
    products_map = products.set_index('id').to_dict('index')
    
    total = 0
    
    for pid, qty in list(st.session_state['cart'].items()):
        if pid in products_map:
            p = products_map[pid]
            total += p['price'] * qty
            
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                st.subheader(p['name'])
            with c2:
                st.write(f"${p['price']}")
            with c3:
                st.write(f"Qty: {qty}")
            with c4:
                if st.button("Remove", key=f"del_{pid}"):
                    st.session_state['cart'] = cart_service.remove_from_cart(st.session_state['cart'], pid)
                    st.rerun()
                    
    st.markdown("---")
    st.subheader(f"Total: ${total:.2f}")
    
    if st.button("Proceed to Checkout"):
        st.session_state['page'] = 'checkout'
        st.rerun()
