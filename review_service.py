from config.settings import RAW_DATA_DIR
from utils.helpers import load_csv, save_csv
import os
import pandas as pd
from datetime import datetime

REVIEWS_FILE = os.path.join(RAW_DATA_DIR, 'reviews.csv')

class ReviewService:
    def __init__(self):
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(REVIEWS_FILE):
            df = pd.DataFrame(columns=['product_id', 'user_id', 'rating', 'comment', 'created_at'])
            save_csv(df, REVIEWS_FILE)

    def add_review(self, product_id, user_id, rating, comment):
        reviews = load_csv(REVIEWS_FILE)
        new_review = pd.DataFrame([{
            'product_id': product_id,
            'user_id': user_id,
            'rating': rating,
            'comment': comment,
            'created_at': datetime.now().isoformat()
        }])
        
        reviews = pd.concat([reviews, new_review], ignore_index=True)
        save_csv(reviews, REVIEWS_FILE)
        return True, "Review added successfully"

    def get_reviews_for_product(self, product_id):
        reviews = load_csv(REVIEWS_FILE)
        if reviews.empty:
            return pd.DataFrame()
        return reviews[reviews['product_id'] == product_id]
