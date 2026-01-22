import os

# Base Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
DB_PATH = os.path.join(BASE_DIR, 'database', 'ecommerce.db')
DB_CONNECTION_STRING = f'sqlite:///{DB_PATH}'

# Data Paths
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# App Settings
APP_TITLE = "Streamlit Ecommerce Store"
APP_ICON = "🛒"
