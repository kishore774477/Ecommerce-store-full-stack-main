import streamlit as st

from models.recommender import RecommenderSystem
from services.cart_service import CartService
from services.order_service import OrderService
from services.product_service import ProductService
from services.review_service import ReviewService
from ui.components import PLACEHOLDER_IMAGE, current_user, go_to, product_card, stock_badge
from utils.helpers import format_price


def show_product_page():
    if st.button("← Back to shop"):
        go_to("home")

    product_id = st.session_state.get("selected_product")
    product_service = ProductService()
    product = product_service.get_product_by_id(product_id) if product_id is not None else None
    if not product:
        st.error("Product not found")
        return

    review_service = ReviewService()
    avg, count = review_service.get_average_rating(product["id"])

    c1, c2 = st.columns([1, 1])
    with c1:
        st.image(product["image"] or PLACEHOLDER_IMAGE, width="stretch")
    with c2:
        st.title(product["name"])
        st.caption(product["category"])
        if avg is not None:
            st.markdown(f"{'⭐' * round(avg)} **{avg}** ({count} review{'s' if count != 1 else ''})")
        st.header(format_price(product["price"]))
        st.write(product["description"])
        st.markdown(stock_badge(product["stock"]))

        cart = st.session_state.setdefault("cart", {})
        in_cart = cart.get(product["id"], 0)
        available = product["stock"] - in_cart
        if in_cart:
            st.caption(f"{in_cart} already in your cart")
        if available > 0:
            qty = st.number_input("Quantity", min_value=1, max_value=int(available), value=1, step=1)
            if st.button("Add to Cart", type="primary"):
                CartService().add_to_cart(cart, product["id"], qty)
                st.toast(f"Added {qty} × {product['name']} to cart")
                st.rerun()
        else:
            st.button("Add to Cart", disabled=True)

    # Reviews
    st.divider()
    st.subheader("Customer reviews")
    user = current_user()
    if user:
        with st.form("review_form", clear_on_submit=True):
            rating = st.select_slider("Your rating", options=[1, 2, 3, 4, 5], value=5)
            comment = st.text_area("Your review", max_chars=500)
            if st.form_submit_button("Submit review"):
                ok, msg = review_service.add_review(product["id"], user["id"], rating, comment, user["username"])
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()
    else:
        st.caption("Sign in to write a review.")

    reviews = review_service.get_reviews_for_product(product["id"])
    if reviews.empty:
        st.info("No reviews yet.")
    for _, r in reviews.iterrows():
        with st.container(border=True):
            st.markdown(f"{'⭐' * int(r['rating'])} — **{r['username']}** · {str(r['created_at'])[:10]}")
            if r["comment"]:
                st.write(r["comment"])

    # Recommendations
    similar = RecommenderSystem(product_service.get_all_products(),
                                OrderService().get_all_orders()).recommend_similar(product["id"], n=4)
    if not similar.empty:
        st.divider()
        st.subheader("You may also like")
        cols = st.columns(4)
        for col, (_, p) in zip(cols, similar.iterrows()):
            with col:
                product_card(p, "sim")
