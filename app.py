import streamlit as st

from config.settings import APP_ICON, APP_TITLE
from services.auth_service import AuthService
from services.cart_service import CartService
from ui.admin_analytics import show_admin_analytics
from ui.admin_dashboard import show_admin_dashboard
from ui.admin_inventory import show_admin_inventory
from ui.admin_orders import show_admin_orders
from ui.cart import show_cart
from ui.checkout import show_checkout
from ui.home import show_home
from ui.login import show_login
from ui.order_history import show_order_history
from ui.product_page import show_product_page
from ui.register import show_register

st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")

# Initialise services once so the data files (and default admin) exist.
AuthService()

# Session state
st.session_state.setdefault("page", "home")
st.session_state.setdefault("cart", {})

PAGES = {
    "home": show_home,
    "login": show_login,
    "register": show_register,
    "product_page": show_product_page,
    "cart": show_cart,
    "checkout": show_checkout,
    "order_history": show_order_history,
    "admin_dashboard": show_admin_dashboard,
    "admin_orders": show_admin_orders,
    "admin_inventory": show_admin_inventory,
    "admin_analytics": show_admin_analytics,
}


def nav_button(label, page, key):
    is_current = st.session_state["page"] == page
    if st.button(label, key=key, width="stretch", type="primary" if is_current else "secondary"):
        st.session_state["page"] = page
        st.rerun()


with st.sidebar:
    st.title(f"{APP_ICON} {APP_TITLE}")
    user = st.session_state.get("user")
    cart_count = CartService().get_item_count(st.session_state["cart"])

    nav_button("🏠 Home", "home", "nav_home")
    nav_button(f"🛒 Cart ({cart_count})", "cart", "nav_cart")

    if user:
        nav_button("📦 My Orders", "order_history", "nav_orders")
        st.markdown("---")
        st.write(f"Signed in as **{user['username']}**")
        if st.button("Sign Out", key="nav_signout", width="stretch"):
            for key in ("user", "next_page", "last_order_id"):
                st.session_state.pop(key, None)
            st.session_state["cart"] = {}
            st.session_state["page"] = "home"
            st.rerun()

        if AuthService.is_admin(user):
            st.markdown("---")
            st.caption("ADMIN PANEL")
            nav_button("📊 Dashboard", "admin_dashboard", "nav_admin")
            nav_button("🧾 Manage Orders", "admin_orders", "nav_admin_orders")
            nav_button("📦 Inventory", "admin_inventory", "nav_admin_inventory")
            nav_button("📈 Analytics", "admin_analytics", "nav_admin_analytics")
    else:
        st.markdown("---")
        nav_button("Sign In", "login", "nav_login")
        nav_button("Register", "register", "nav_register")

# Routing
PAGES.get(st.session_state["page"], show_home)()
