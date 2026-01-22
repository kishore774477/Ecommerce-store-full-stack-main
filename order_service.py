from config.settings import RAW_DATA_DIR
from utils.helpers import load_csv, save_csv
import os
import pandas as pd
from datetime import datetime

ORDERS_FILE = os.path.join(RAW_DATA_DIR, 'orders.csv')

class OrderService:
    def __init__(self):
        self._ensure_orders_file()

    def _ensure_orders_file(self):
        if not os.path.exists(ORDERS_FILE):
            df = pd.DataFrame(columns=['id', 'user_id', 'total_amount', 'status', 'created_at', 'items'])
            save_csv(df, ORDERS_FILE)

    def create_order(self, user_id, cart_items, total_amount):
        orders = load_csv(ORDERS_FILE)
        new_order = pd.DataFrame([{
            'id': len(orders) + 1,
            'user_id': user_id,
            'total_amount': total_amount,
            'status': 'Pending',
            'created_at': datetime.now().isoformat(),
            'items': str(cart_items) # Simplified storage
        }])
        
        orders = pd.concat([orders, new_order], ignore_index=True)
        save_csv(orders, ORDERS_FILE)
        return True, "Order placed successfully"
