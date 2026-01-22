from config.settings import RAW_DATA_DIR
from utils.helpers import load_csv, save_csv
import os
import pandas as pd

PRODUCTS_FILE = os.path.join(RAW_DATA_DIR, 'products.csv')

class InventoryService:
    def __init__(self):
        # We assume inventory is tracked in products.csv for simplicity in this file structure
        self._ensure_stock_column()

    def _ensure_stock_column(self):
        if os.path.exists(PRODUCTS_FILE):
            df = load_csv(PRODUCTS_FILE)
            if 'stock' not in df.columns:
                df['stock'] = 100 # Default initial stock
                save_csv(df, PRODUCTS_FILE)

    def get_stock(self, product_id):
        df = load_csv(PRODUCTS_FILE)
        product = df[df['id'] == product_id]
        if not product.empty:
            return int(product.iloc[0]['stock'])
        return 0

    def update_stock(self, product_id, quantity_change):
        df = load_csv(PRODUCTS_FILE)
        idx = df.index[df['id'] == product_id]
        if not idx.empty:
            # Check if stock would be negative
            current_stock = df.at[idx[0], 'stock']
            new_stock = current_stock + quantity_change
            if new_stock < 0:
                return False, "Insufficient stock"
            
            df.at[idx[0], 'stock'] = new_stock
            save_csv(df, PRODUCTS_FILE)
            return True, "Stock updated"
        return False, "Product not found"
