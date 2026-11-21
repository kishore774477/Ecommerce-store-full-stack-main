from config.settings import LOW_STOCK_THRESHOLD, PRODUCTS_FILE
from services.product_service import PRODUCT_COLUMNS, ProductService
from utils.helpers import data_lock, save_csv


class InventoryService:
    """Stock is tracked in the `stock` column of products.csv."""

    def __init__(self):
        self.product_service = ProductService()

    def get_stock(self, product_id) -> int:
        product = self.product_service.get_product_by_id(product_id)
        return product["stock"] if product else 0

    def update_stock(self, product_id, quantity_change):
        with data_lock:
            df = self.product_service.get_all_products()
            idx = df.index[df["id"] == int(product_id)]
            if idx.empty:
                return False, "Product not found"
            new_stock = int(df.at[idx[0], "stock"]) + int(quantity_change)
            if new_stock < 0:
                return False, "Insufficient stock"
            df.at[idx[0], "stock"] = new_stock
            save_csv(df[PRODUCT_COLUMNS], PRODUCTS_FILE)
        return True, f"Stock updated to {new_stock}"

    def check_availability(self, cart: dict):
        """Returns (ok, message) for a {product_id: qty} cart."""
        df = self.product_service.get_all_products()
        stock = dict(zip(df["id"], df["stock"]))
        names = dict(zip(df["id"], df["name"]))
        for pid, qty in cart.items():
            pid = int(pid)
            if pid not in stock:
                return False, f"Product #{pid} is no longer available"
            if qty > stock[pid]:
                return False, f"Only {stock[pid]} left of {names[pid]}"
        return True, "OK"

    def deduct_for_cart(self, cart: dict):
        """Atomically checks and deducts stock for every cart line."""
        with data_lock:
            ok, msg = self.check_availability(cart)
            if not ok:
                return False, msg
            df = self.product_service.get_all_products()
            for pid, qty in cart.items():
                idx = df.index[df["id"] == int(pid)][0]
                df.at[idx, "stock"] = int(df.at[idx, "stock"]) - int(qty)
            save_csv(df[PRODUCT_COLUMNS], PRODUCTS_FILE)
        return True, "Stock reserved"

    def restock_for_cart(self, cart: dict):
        """Puts stock back, e.g. when an order is cancelled."""
        with data_lock:
            df = self.product_service.get_all_products()
            for pid, qty in cart.items():
                idx = df.index[df["id"] == int(pid)]
                if not idx.empty:
                    df.at[idx[0], "stock"] = int(df.at[idx[0], "stock"]) + int(qty)
            save_csv(df[PRODUCT_COLUMNS], PRODUCTS_FILE)

    def get_low_stock(self, threshold: int = LOW_STOCK_THRESHOLD):
        df = self.product_service.get_all_products()
        return df[df["stock"] <= threshold][["id", "name", "stock"]]
