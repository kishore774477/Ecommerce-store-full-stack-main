import os
import shutil

import pandas as pd

from config.settings import PRODUCTS_FILE, SEED_PRODUCTS_FILE
from utils.helpers import data_lock, load_csv, next_id, save_csv

PRODUCT_COLUMNS = ["id", "name", "price", "category", "description", "image", "stock"]


class ProductService:
    def __init__(self):
        self._ensure_products_file()

    def _ensure_products_file(self):
        with data_lock:
            if os.path.exists(PRODUCTS_FILE):
                return
            if os.path.exists(SEED_PRODUCTS_FILE):
                shutil.copyfile(SEED_PRODUCTS_FILE, PRODUCTS_FILE)
            else:
                save_csv(pd.DataFrame(columns=PRODUCT_COLUMNS), PRODUCTS_FILE)

    def get_all_products(self) -> pd.DataFrame:
        df = load_csv(PRODUCTS_FILE)
        if df.empty:
            return pd.DataFrame(columns=PRODUCT_COLUMNS)
        if "stock" not in df.columns:
            df["stock"] = 100
        df["id"] = df["id"].astype(int)
        df["stock"] = df["stock"].fillna(0).astype(int)
        for col in ("description", "image"):
            df[col] = df[col].astype("string").fillna("").astype(str)
        return df.reset_index(drop=True)

    def get_categories(self) -> list:
        df = self.get_all_products()
        return sorted(df["category"].dropna().unique().tolist()) if not df.empty else []

    def search_products(self, query: str = "", category: str = None,
                        min_price: float = None, max_price: float = None,
                        sort_by: str = None) -> pd.DataFrame:
        df = self.get_all_products()
        if df.empty:
            return df
        if query:
            q = query.strip().lower()
            mask = df["name"].str.lower().str.contains(q, regex=False) | \
                df["description"].str.lower().str.contains(q, regex=False)
            df = df[mask]
        if category and category != "All":
            df = df[df["category"] == category]
        if min_price is not None:
            df = df[df["price"] >= min_price]
        if max_price is not None:
            df = df[df["price"] <= max_price]
        if sort_by == "Price: Low to High":
            df = df.sort_values("price")
        elif sort_by == "Price: High to Low":
            df = df.sort_values("price", ascending=False)
        elif sort_by == "Name":
            df = df.sort_values("name")
        return df.reset_index(drop=True)

    def get_product_by_id(self, product_id):
        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return None
        products = self.get_all_products()
        product = products[products["id"] == product_id]
        if product.empty:
            return None
        row = product.iloc[0]
        return {
            "id": int(row["id"]),
            "name": str(row["name"]),
            "price": float(row["price"]),
            "category": str(row["category"]),
            "description": str(row["description"]),
            "image": str(row["image"]),
            "stock": int(row["stock"]),
        }

    def add_product(self, name, price, category, description="", image="", stock=0):
        if not name or price is None or float(price) <= 0:
            return False, "Name and a positive price are required", None
        if int(stock) < 0:
            return False, "Stock cannot be negative", None
        with data_lock:
            df = self.get_all_products()
            new_id = next_id(df)
            row = pd.DataFrame([{
                "id": new_id, "name": name.strip(), "price": round(float(price), 2),
                "category": category.strip() or "General", "description": description,
                "image": image, "stock": int(stock),
            }])
            df = pd.concat([df, row], ignore_index=True) if not df.empty else row
            save_csv(df[PRODUCT_COLUMNS], PRODUCTS_FILE)
        return True, f"Product '{name}' added", new_id

    def delete_product(self, product_id):
        with data_lock:
            df = self.get_all_products()
            if int(product_id) not in df["id"].values:
                return False, "Product not found"
            df = df[df["id"] != int(product_id)]
            save_csv(df[PRODUCT_COLUMNS], PRODUCTS_FILE)
        return True, "Product deleted"
