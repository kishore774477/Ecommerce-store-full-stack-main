import pandas as pd
from collections import Counter

class RecommenderSystem:
    def __init__(self, products_df, orders_df):
        self.products_df = products_df
        self.orders_df = orders_df

    def recommend_popular(self, n=5):
        """Recommend most popular products based on order frequency."""
        if self.orders_df.empty:
            return self.products_df.head(n)
            
        all_items = []
        for items_str in self.orders_df['items']:
            # items_str is stored as string representation of dict, naive parsing for demo
            try:
                items_dict = eval(items_str)
                all_items.extend(items_dict.keys())
            except:
                continue
                
        counter = Counter(all_items)
        most_common_ids = [item[0] for item in counter.most_common(n)]
        
        # Filter products that match IDs
        recommendations = self.products_df[self.products_df['id'].isin(most_common_ids)]
        
        # If not enough data, pad with top products
        if len(recommendations) < n:
            remaining = self.products_df[~self.products_df['id'].isin(most_common_ids)].head(n - len(recommendations))
            recommendations = pd.concat([recommendations, remaining])
            
        return recommendations
