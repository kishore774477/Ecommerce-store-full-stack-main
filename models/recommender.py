from collections import Counter
from itertools import combinations

import pandas as pd

from utils.helpers import parse_items


class RecommenderSystem:
    def __init__(self, products_df: pd.DataFrame, orders_df: pd.DataFrame):
        self.products_df = products_df
        self.orders_df = orders_df if orders_df is not None else pd.DataFrame()
        self._baskets = [
            parse_items(items) for items in self.orders_df.get("items", pd.Series(dtype=str))
        ]

    def recommend_popular(self, n=5) -> pd.DataFrame:
        """Most popular products by units ordered, padded with in-stock products."""
        counter = Counter()
        for basket in self._baskets:
            for pid, qty in basket.items():
                counter[pid] += qty
        ranked_ids = [pid for pid, _ in counter.most_common()]
        available = self.products_df[self.products_df["stock"] > 0] \
            if "stock" in self.products_df.columns else self.products_df
        ranked = available.set_index("id").reindex(
            [i for i in ranked_ids if i in set(available["id"])]).reset_index()
        if len(ranked) < n:
            rest = available[~available["id"].isin(ranked["id"])].head(n - len(ranked))
            ranked = pd.concat([ranked, rest], ignore_index=True)
        return ranked.head(n)

    def recommend_similar(self, product_id, n=4) -> pd.DataFrame:
        """'Frequently bought together' first, then products from the same category."""
        product_id = int(product_id)
        together = Counter()
        for basket in self._baskets:
            if product_id in basket:
                for other in basket:
                    if other != product_id:
                        together[other] += 1
        ids = [pid for pid, _ in together.most_common(n)]

        row = self.products_df[self.products_df["id"] == product_id]
        if not row.empty and len(ids) < n:
            category = row.iloc[0]["category"]
            same_cat = self.products_df[
                (self.products_df["category"] == category) &
                (self.products_df["id"] != product_id) &
                (~self.products_df["id"].isin(ids))
            ]["id"].tolist()
            ids += same_cat[: n - len(ids)]
        result = self.products_df.set_index("id").reindex(ids).dropna(subset=["name"]).reset_index()
        return result.head(n)

    def frequently_bought_pairs(self, n=5):
        pairs = Counter()
        for basket in self._baskets:
            for a, b in combinations(sorted(basket), 2):
                pairs[(a, b)] += 1
        return pairs.most_common(n)
