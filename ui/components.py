import streamlit as st

from services.auth_service import AuthService
from services.cart_service import CartService
from utils.helpers import format_price

PLACEHOLDER_IMAGE = "https://placehold.co/400x300?text=No+Image"


def go_to(page: str, **state):
    """Switches page and reruns the script."""
    for key, value in state.items():
        st.session_state[key] = value
    st.session_state["page"] = page
    st.rerun()


def flash(message: str, kind: str = "success"):
    """Queues a message that survives the next st.rerun()."""
    st.session_state["flash"] = (kind, message)


def show_flash():
    if "flash" in st.session_state:
        kind, message = st.session_state.pop("flash")
        getattr(st, kind, st.info)(message)


def current_user():
    return st.session_state.get("user")


def require_login(message="Please sign in to continue") -> bool:
    if current_user():
        return True
    st.warning(message)
    if st.button("Sign In", key="require_login_btn"):
        go_to("login", next_page=st.session_state.get("page", "home"))
    return False


def require_admin() -> bool:
    if AuthService.is_admin(current_user()):
        return True
    st.error("Access denied: admin only.")
    return False


def stock_badge(stock: int) -> str:
    if stock <= 0:
        return ":red[Out of stock]"
    if stock <= 5:
        return f":orange[Only {stock} left]"
    return ":green[In stock]"


def product_card(product, key_prefix: str):
    """Renders one product tile with View + Add to cart buttons."""
    with st.container(border=True):
        st.image(product["image"] or PLACEHOLDER_IMAGE, width="stretch")
        st.markdown(f"**{product['name']}**")
        st.caption(product["category"])
        st.markdown(f"#### {format_price(product['price'])}")
        st.markdown(stock_badge(int(product["stock"])))
        c1, c2 = st.columns(2)
        pid = int(product["id"])
        if c1.button("View", key=f"{key_prefix}_view_{pid}", width="stretch"):
            go_to("product_page", selected_product=pid)
        in_cart = st.session_state.get("cart", {}).get(pid, 0)
        disabled = int(product["stock"]) <= in_cart
        if c2.button("Add 🛒", key=f"{key_prefix}_add_{pid}", width="stretch",
                     disabled=disabled, type="primary"):
            CartService().add_to_cart(st.session_state.setdefault("cart", {}), pid)
            st.toast(f"Added {product['name']} to cart")
            st.rerun()
