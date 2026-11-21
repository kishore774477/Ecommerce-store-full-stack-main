from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.auth_service import AuthService
from services.order_service import OrderService
from services.product_service import ProductService

from .routes import auth, orders, products

# Make sure data files (seed products, default admin) exist on startup.
ProductService()
AuthService()
OrderService()

app = FastAPI(
    title="Ecommerce API",
    description="REST API sharing the same data as the Streamlit store.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Ecommerce API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
