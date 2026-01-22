import pandas as pd

class AnalyticsEngine:
    def __init__(self, orders_df):
        self.orders_df = orders_df

    def get_total_sales(self):
        if self.orders_df.empty:
            return 0.0
        return self.orders_df['total_amount'].sum()

    def get_orders_count(self):
        return len(self.orders_df)

    def get_sales_over_time(self):
        if self.orders_df.empty:
            return pd.DataFrame()
        
        df = self.orders_df.copy()
        df['created_at'] = pd.to_datetime(df['created_at'])
        return df.groupby(df['created_at'].dt.date)['total_amount'].sum()
