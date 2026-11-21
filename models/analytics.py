from collections import Counter

import pandas as pd

from utils.helpers import parse_items


class AnalyticsEngine:
    def __init__(self, orders_df: pd.DataFrame, products_df: pd.DataFrame = None):
        orders_df = orders_df if orders_df is not None else pd.DataFrame()
        # Cancelled orders don't count as revenue.
        if not orders_df.empty and "status" in orders_df.columns:
            self.all_orders = orders_df
            self.orders_df = orders_df[orders_df["status"] != "Cancelled"]
        else:
            self.all_orders = orders_df
            self.orders_df = orders_df
        self.products_df = products_df if products_df is not None else pd.DataFrame()

    def get_total_sales(self) -> float:
        if self.orders_df.empty:
            return 0.0
        return float(self.orders_df["total_amount"].sum())

    def get_orders_count(self) -> int:
        return len(self.orders_df)

    def get_average_order_value(self) -> float:
        count = self.get_orders_count()
        return self.get_total_sales() / count if count else 0.0

    def get_sales_over_time(self) -> pd.DataFrame:
        if self.orders_df.empty:
            return pd.DataFrame(columns=["date", "revenue"])
        df = self.orders_df.copy()
        df["date"] = pd.to_datetime(df["created_at"]).dt.date
        return df.groupby("date", as_index=False)["total_amount"].sum().rename(
            columns={"total_amount": "revenue"})

    def get_status_counts(self) -> pd.DataFrame:
        if self.all_orders.empty:
            return pd.DataFrame(columns=["status", "orders"])
        counts = self.all_orders["status"].value_counts()
        return pd.DataFrame({"status": counts.index, "orders": counts.values})

    def get_top_products(self, n: int = 5) -> pd.DataFrame:
        """Units sold and revenue per product."""
        if self.orders_df.empty:
            return pd.DataFrame(columns=["name", "units_sold", "revenue"])
        units = Counter()
        for items in self.orders_df["items"]:
            for pid, qty in parse_items(items).items():
                units[pid] += qty
        if not units:
            return pd.DataFrame(columns=["name", "units_sold", "revenue"])
        df = pd.DataFrame(units.items(), columns=["id", "units_sold"])
        if not self.products_df.empty:
            df = df.merge(self.products_df[["id", "name", "price"]], on="id", how="left")
            df["name"] = df["name"].fillna(df["id"].map(lambda i: f"Product #{i}"))
            df["revenue"] = df["units_sold"] * df["price"].fillna(0)
        else:
            df["name"] = df["id"].map(lambda i: f"Product #{i}")
            df["revenue"] = 0.0
        return df.sort_values("units_sold", ascending=False).head(n)[["name", "units_sold", "revenue"]]

    def get_sales_by_category(self) -> pd.DataFrame:
        top = self.get_top_products(n=10_000)
        if top.empty or self.products_df.empty:
            return pd.DataFrame(columns=["category", "revenue"])
        merged = top.merge(self.products_df[["name", "category"]], on="name", how="left")
        return merged.groupby("category", as_index=False)["revenue"].sum().sort_values(
            "revenue", ascending=False)
