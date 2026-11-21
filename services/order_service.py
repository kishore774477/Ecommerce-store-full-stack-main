import json
import os
from datetime import datetime

import pandas as pd

from config.settings import ORDER_STATUSES, ORDERS_FILE
from services.cart_service import CartService
from services.inventory_service import InventoryService
from services.product_service import ProductService
from utils.helpers import data_lock, load_csv, next_id, parse_items, save_csv

ORDER_COLUMNS = ["id", "user_id", "total_amount", "status", "created_at", "items",
                 "address", "payment_method", "payment_ref"]


class OrderService:
    def __init__(self):
        self._ensure_orders_file()
        self.product_service = ProductService()
        self.inventory_service = InventoryService()

    def _ensure_orders_file(self):
        with data_lock:
            if not os.path.exists(ORDERS_FILE):
                save_csv(pd.DataFrame(columns=ORDER_COLUMNS), ORDERS_FILE)

    def get_all_orders(self) -> pd.DataFrame:
        df = load_csv(ORDERS_FILE)
        if df.empty:
            return pd.DataFrame(columns=ORDER_COLUMNS)
        for col in ORDER_COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df["id"] = df["id"].astype(int)
        df["user_id"] = df["user_id"].astype(int)
        df["total_amount"] = df["total_amount"].astype(float)
        for col in ("address", "payment_method", "payment_ref"):
            df[col] = df[col].astype("string").fillna("").astype(str)
        return df[ORDER_COLUMNS]

    def get_orders_for_user(self, user_id) -> pd.DataFrame:
        df = self.get_all_orders()
        return df[df["user_id"] == int(user_id)].sort_values("created_at", ascending=False)

    def describe_items(self, items) -> list:
        """Turns the stored items column into readable lines."""
        products = self.product_service.get_all_products()
        names = dict(zip(products["id"], products["name"])) if not products.empty else {}
        prices = dict(zip(products["id"], products["price"])) if not products.empty else {}
        lines = []
        for pid, qty in parse_items(items).items():
            lines.append({
                "product_id": pid,
                "name": names.get(pid, f"Product #{pid} (removed)"),
                "quantity": qty,
                "price": float(prices.get(pid, 0.0)),
            })
        return lines

    def create_order(self, user_id, cart_items: dict, address: str,
                     payment_method: str = "Card", payment_ref: str = ""):
        if not cart_items:
            return False, "Cart is empty", None
        if not address or not address.strip():
            return False, "Please provide a delivery address", None

        cart = {int(k): int(v) for k, v in cart_items.items() if int(v) > 0}
        with data_lock:
            ok, msg = self.inventory_service.deduct_for_cart(cart)
            if not ok:
                return False, msg, None

            # Price is computed server-side from the catalogue, never trusted from the client.
            total = CartService().get_cart_total(cart, self.product_service)
            orders = self.get_all_orders()
            order_id = next_id(orders)
            new_order = pd.DataFrame([{
                "id": order_id,
                "user_id": int(user_id),
                "total_amount": total,
                "status": "Pending",
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "items": json.dumps({str(k): v for k, v in cart.items()}),
                "address": address.strip(),
                "payment_method": payment_method,
                "payment_ref": payment_ref,
            }])
            orders = pd.concat([orders, new_order], ignore_index=True) if not orders.empty else new_order
            save_csv(orders[ORDER_COLUMNS], ORDERS_FILE)
        return True, f"Order #{order_id} placed successfully", order_id

    def update_status(self, order_id, new_status):
        if new_status not in ORDER_STATUSES:
            return False, "Invalid status"
        with data_lock:
            orders = self.get_all_orders()
            idx = orders.index[orders["id"] == int(order_id)]
            if idx.empty:
                return False, "Order ID not found"
            old_status = orders.at[idx[0], "status"]
            if old_status == new_status:
                return True, f"Order #{order_id} is already {new_status}"
            if old_status == "Cancelled":
                return False, "Cancelled orders cannot be changed"
            if new_status == "Cancelled":
                self.inventory_service.restock_for_cart(parse_items(orders.at[idx[0], "items"]))
            orders.at[idx[0], "status"] = new_status
            save_csv(orders, ORDERS_FILE)
        return True, f"Order #{order_id} updated to {new_status}"

    def cancel_order(self, order_id, user_id):
        """Customers may cancel their own orders while still Pending."""
        orders = self.get_all_orders()
        row = orders[(orders["id"] == int(order_id)) & (orders["user_id"] == int(user_id))]
        if row.empty:
            return False, "Order not found"
        if row.iloc[0]["status"] != "Pending":
            return False, "Only pending orders can be cancelled"
        return self.update_status(order_id, "Cancelled")
