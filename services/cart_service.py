class CartService:
    """Stateless helpers over a {product_id: quantity} dict kept in st.session_state."""

    def add_to_cart(self, session_cart, product_id, quantity=1):
        product_id = int(product_id)
        session_cart[product_id] = session_cart.get(product_id, 0) + int(quantity)
        return session_cart

    def update_quantity(self, session_cart, product_id, quantity):
        product_id = int(product_id)
        if quantity <= 0:
            session_cart.pop(product_id, None)
        else:
            session_cart[product_id] = int(quantity)
        return session_cart

    def remove_from_cart(self, session_cart, product_id):
        session_cart.pop(int(product_id), None)
        return session_cart

    def get_item_count(self, session_cart) -> int:
        return sum(session_cart.values()) if session_cart else 0

    def get_cart_items(self, session_cart, product_service):
        """Returns a list of cart lines enriched with product details."""
        products = product_service.get_all_products()
        if products.empty:
            return []
        product_map = products.set_index("id").to_dict("index")
        items = []
        for pid, qty in session_cart.items():
            p = product_map.get(int(pid))
            if not p:
                continue
            items.append({
                "id": int(pid),
                "name": p["name"],
                "price": float(p["price"]),
                "image": p["image"],
                "stock": int(p["stock"]),
                "quantity": int(qty),
                "subtotal": float(p["price"]) * int(qty),
            })
        return items

    def get_cart_total(self, session_cart, product_service):
        return round(sum(i["subtotal"] for i in self.get_cart_items(session_cart, product_service)), 2)
