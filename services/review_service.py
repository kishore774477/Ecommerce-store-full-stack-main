import os
from datetime import datetime

import pandas as pd

from config.settings import REVIEWS_FILE
from utils.helpers import data_lock, load_csv, save_csv

REVIEW_COLUMNS = ["product_id", "user_id", "username", "rating", "comment", "created_at"]


class ReviewService:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        with data_lock:
            if not os.path.exists(REVIEWS_FILE):
                save_csv(pd.DataFrame(columns=REVIEW_COLUMNS), REVIEWS_FILE)

    def _load(self) -> pd.DataFrame:
        df = load_csv(REVIEWS_FILE)
        if df.empty:
            return pd.DataFrame(columns=REVIEW_COLUMNS)
        if "username" not in df.columns:
            df["username"] = "Customer"
        df["comment"] = df["comment"].astype("string").fillna("").astype(str)
        return df[REVIEW_COLUMNS]

    def add_review(self, product_id, user_id, rating, comment, username="Customer"):
        rating = int(rating)
        if rating < 1 or rating > 5:
            return False, "Rating must be between 1 and 5"
        with data_lock:
            reviews = self._load()
            # One review per user per product: replace the previous one.
            reviews = reviews[~((reviews["product_id"] == int(product_id)) &
                                (reviews["user_id"] == int(user_id)))]
            new_review = pd.DataFrame([{
                "product_id": int(product_id),
                "user_id": int(user_id),
                "username": username,
                "rating": rating,
                "comment": (comment or "").strip(),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }])
            reviews = pd.concat([reviews, new_review], ignore_index=True) if not reviews.empty else new_review
            save_csv(reviews, REVIEWS_FILE)
        return True, "Review saved. Thank you!"

    def get_reviews_for_product(self, product_id) -> pd.DataFrame:
        reviews = self._load()
        if reviews.empty:
            return reviews
        return reviews[reviews["product_id"] == int(product_id)].sort_values("created_at", ascending=False)

    def get_average_rating(self, product_id):
        reviews = self.get_reviews_for_product(product_id)
        if reviews.empty:
            return None, 0
        return round(float(reviews["rating"].mean()), 1), len(reviews)
