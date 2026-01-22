from fastapi import FastAPI
from .database import engine, Base
from .routes import products, auth

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Ecommerce API")

app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Ecommerce API"}
