import streamlit as st

from services.inventory_service import InventoryService
from services.product_service import ProductService
from ui.components import require_admin


def show_admin_inventory():
    st.title("Inventory Management")
    if not require_admin():
        return

    product_service = ProductService()
    inventory_service = InventoryService()
    products = product_service.get_all_products()

    if products.empty:
        st.info("No products found")
    else:
        st.dataframe(
            products[["id", "name", "category", "price", "stock"]],
            hide_index=True, width="stretch",
            column_config={"price": st.column_config.NumberColumn(format="$%.2f")},
        )

        st.subheader("Update Stock")
        c1, c2, c3 = st.columns([3, 2, 1], vertical_alignment="bottom")
        names = dict(zip(products["id"], products["name"]))
        selected_id = c1.selectbox("Product", products["id"].tolist(),
                                   format_func=lambda i: f"#{i} · {names[i]}")
        qty_change = c2.number_input("Add (+) / Remove (−) quantity", step=1, value=0)
        if c3.button("Update", type="primary"):
            success, msg = inventory_service.update_stock(selected_id, qty_change)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    st.subheader("Add New Product")
    with st.form("add_product", clear_on_submit=True):
        c1, c2 = st.columns(2)
        name = c1.text_input("Name")
        category = c2.text_input("Category")
        c3, c4 = st.columns(2)
        price = c3.number_input("Price", min_value=0.0, step=1.0, format="%.2f")
        stock = c4.number_input("Initial stock", min_value=0, step=1, value=10)
        image = st.text_input("Image URL (optional)")
        description = st.text_area("Description")
        if st.form_submit_button("Add product", type="primary"):
            ok, msg, _ = product_service.add_product(name, price, category, description, image, stock)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    if not products.empty:
        with st.expander("Delete a product"):
            names = dict(zip(products["id"], products["name"]))
            del_id = st.selectbox("Product to delete", products["id"].tolist(),
                                  format_func=lambda i: f"#{i} · {names[i]}", key="del_product")
            if st.button("Delete product", type="secondary"):
                ok, msg = product_service.delete_product(del_id)
                (st.success if ok else st.error)(msg)
                if ok:
                    st.rerun()
