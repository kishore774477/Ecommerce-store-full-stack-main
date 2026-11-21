import streamlit as st

from models.recommender import RecommenderSystem
from services.order_service import OrderService
from services.product_service import ProductService
from ui.components import product_card, show_flash

PER_ROW = 3


def _grid(products, key_prefix):
    rows = [products.iloc[i:i + PER_ROW] for i in range(0, len(products), PER_ROW)]
    for chunk in rows:
        cols = st.columns(PER_ROW)
        for col, (_, product) in zip(cols, chunk.iterrows()):
            with col:
                product_card(product, key_prefix)


def show_home():
    show_flash()
    st.title("Welcome to Our Store")

    product_service = ProductService()
    all_products = product_service.get_all_products()
    if all_products.empty:
        st.info("No products available.")
        return

    # Filters
    with st.container(border=True):
        c1, c2, c3 = st.columns([3, 2, 2])
        query = c1.text_input("Search products", placeholder="e.g. laptop, watch, cricket")
        category = c2.selectbox("Category", ["All"] + product_service.get_categories())
        sort_by = c3.selectbox("Sort by", ["Featured", "Price: Low to High", "Price: High to Low", "Name"])
        max_price = float(all_products["price"].max())
        price_range = st.slider("Price range", 0.0, max_price, (0.0, max_price), step=10.0)

    filtering = bool(query) or category != "All" or price_range != (0.0, max_price)

    if not filtering:
        orders = OrderService().get_all_orders()
        popular = RecommenderSystem(all_products, orders).recommend_popular(n=PER_ROW)
        if not popular.empty:
            st.subheader("🔥 Popular right now")
            _grid(popular, "pop")
            st.divider()

    products = product_service.search_products(
        query=query, category=category,
        min_price=price_range[0], max_price=price_range[1], sort_by=sort_by,
    )
    st.subheader(f"All products ({len(products)})" if not filtering else f"Results ({len(products)})")
    if products.empty:
        st.info("No products match your filters.")
        return
    _grid(products, "all")
