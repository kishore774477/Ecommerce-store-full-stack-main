import streamlit as st
from config.settings import APP_TITLE, APP_ICON
from ui.login import show_login
from ui.register import show_register
from ui.home import show_home
from ui.product_page import show_product_page
from ui.cart import show_cart
from ui.checkout import show_checkout
from ui.admin_dashboard import show_admin_dashboard

from ui.order_history import show_order_history
from ui.admin_orders import show_admin_orders
from ui.admin_inventory import show_admin_inventory
from ui.admin_analytics import show_admin_analytics

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

# Initialize Session State
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
if 'cart' not in st.session_state:
    st.session_state['cart'] = {}

# Sidebar Navigation
with st.sidebar:
    st.title(APP_TITLE)
    
    if st.button("Home", key="nav_home"):
        st.session_state['page'] = 'home'
        st.rerun()
        
    if 'user' in st.session_state:
        st.write(f"Hello, {st.session_state['user']['username']}!")
        if st.button("Cart", key="nav_cart"):
            st.session_state['page'] = 'cart'
            st.rerun()
        if st.button("My Orders", key="nav_orders"):
            st.session_state['page'] = 'order_history'
            st.rerun()
        if st.button("Sign Out", key="nav_signout"):
            del st.session_state['user']
            st.session_state['page'] = 'login'
            st.rerun()
            
        if st.session_state['user'].get('username') == 'admin':
             st.markdown("---")
             st.write("Admin Panel")
             if st.button("Dashboard", key="nav_admin"):
                st.session_state['page'] = 'admin_dashboard'
                st.rerun()
             if st.button("Manage Orders", key="nav_admin_orders"):
                st.session_state['page'] = 'admin_orders'
                st.rerun()
             if st.button("Inventory", key="nav_admin_inventory"):
                st.session_state['page'] = 'admin_inventory'
                st.rerun()
             if st.button("Analytics", key="nav_admin_analytics"):
                st.session_state['page'] = 'admin_analytics'
                st.rerun()
    else:
        if st.button("Sign In", key="nav_login"):
            st.session_state['page'] = 'login'
            st.rerun()
        if st.button("Register", key="nav_register"):
            st.session_state['page'] = 'register'
            st.rerun()

# Routing
page = st.session_state['page']

if page == 'home':
    show_home()
elif page == 'login':
    show_login()
elif page == 'register':
    show_register()
elif page == 'product_page':
    show_product_page()
elif page == 'cart':
    show_cart()
elif page == 'checkout':
    show_checkout()
elif page == 'order_history':
    show_order_history()
elif page == 'admin_dashboard':
    show_admin_dashboard()
elif page == 'admin_orders':
    show_admin_orders()
elif page == 'admin_inventory':
    show_admin_inventory()
elif page == 'admin_analytics':
    show_admin_analytics()
else:
    show_home()
