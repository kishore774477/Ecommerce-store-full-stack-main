import os

# Base Directory (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data Paths (ECOM_DATA_DIR lets tests / Docker point at another folder)
DATA_DIR = os.environ.get("ECOM_DATA_DIR", os.path.join(BASE_DIR, "data"))
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
SEED_PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "seed_products.csv")

USERS_FILE = os.path.join(RAW_DATA_DIR, "users.csv")
PRODUCTS_FILE = os.path.join(RAW_DATA_DIR, "products.csv")
ORDERS_FILE = os.path.join(RAW_DATA_DIR, "orders.csv")
REVIEWS_FILE = os.path.join(RAW_DATA_DIR, "reviews.csv")

for _d in (RAW_DATA_DIR, PROCESSED_DATA_DIR):
    os.makedirs(_d, exist_ok=True)

# Default admin account, created on first run (override with env vars)
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@store.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# Store Settings
APP_TITLE = "Streamlit Ecommerce Store"
APP_ICON = "🛒"
CURRENCY = "$"
LOW_STOCK_THRESHOLD = 5
ORDER_STATUSES = ["Pending", "Shipped", "Delivered", "Cancelled"]
