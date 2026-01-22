import pandas as pd
import os

def load_csv(file_path: str) -> pd.DataFrame:
    """Loads a CSV file into a pandas DataFrame."""
    if not os.path.exists(file_path):
        return pd.DataFrame()
    return pd.read_csv(file_path)

def save_csv(df: pd.DataFrame, file_path: str):
    """Saves a pandas DataFrame to a CSV file."""
    df.to_csv(file_path, index=False)
