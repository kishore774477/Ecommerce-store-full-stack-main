class CartService:
    def __init__(self):
        # In a real app, this might be stored in a DB or session
        # For Streamlit, we often use st.session_state, so this service might happen to just manipulate that or be a stateless helper.
        pass

    def add_to_cart(self, session_cart, product_id, quantity=1):
        if product_id in session_cart:
            session_cart[product_id] += quantity
        else:
            session_cart[product_id] = quantity
        return session_cart

    def remove_from_cart(self, session_cart, product_id):
        if product_id in session_cart:
            del session_cart[product_id]
        return session_cart

    def get_cart_total(self, session_cart, product_service):
        total = 0
        products = product_service.get_all_products()
        # Convert to dictionary for faster lookup
        product_map = products.set_index('id')['price'].to_dict()
        
        for pid, qty in session_cart.items():
            if pid in product_map:
                total += product_map[pid] * qty
        return total
