from config.settings import RAW_DATA_DIR
from utils.helpers import load_csv
import os
import pandas as pd

PRODUCTS_FILE = os.path.join(RAW_DATA_DIR, 'products.csv')

class ProductService:
    def __init__(self):
        self._ensure_products_file()

    def _ensure_products_file(self):
        if not os.path.exists(PRODUCTS_FILE):
             # Initialize with some dummy data
            df = pd.DataFrame({
                'id': [1, 2, 3],
                'name': ['Laptop', 'Headphones', 'Mouse'],
                'price': [999.99, 199.99, 29.99],
                'category': ['Electronics', 'Electronics', 'Electronics'],
                'description': ['High performance laptop', 'Noise cancelling', 'Wireless mouse'],
                'image': ['https://via.placeholder.com/150', 'https://via.placeholder.com/150', 'https://via.placeholder.com/150']
            })
            df.to_csv(PRODUCTS_FILE, index=False)

    def get_all_products(self):
        return load_csv(PRODUCTS_FILE)

    def get_product_by_id(self, product_id):
        products = load_csv(PRODUCTS_FILE)
        product = products[products['id'] == product_id]
        if not product.empty:
            return product.iloc[0].to_dict()
        return None
