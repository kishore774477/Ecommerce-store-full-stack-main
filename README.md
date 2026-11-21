# Ecommerce Store — Full Stack (Streamlit + FastAPI)

A full-stack e-commerce application with a **Streamlit** storefront and admin panel, a **FastAPI** REST API, and a shared service layer. Both front ends read and write the same data, so an order placed in the UI shows up in the API immediately.

## Features

**Customers**
- Browse 20 seeded products with images, search, category / price filters and sorting
- "Popular right now" and "You may also like" recommendations (order-history based)
- Product pages with stock status, quantity picker and star-rated reviews
- Cart with quantity editing, stock checks and live totals
- Checkout with address + demo card payment (Luhn / expiry / CVV validation) or Cash on Delivery
- Order history with item details and cancellation of pending orders (stock is returned)

**Admins**
- Dashboard: sales, orders, products, customers, sales trend, low-stock alerts, recent orders
- Order management: filter by status, update status (Pending → Shipped → Delivered / Cancelled)
- Inventory: adjust stock, add and delete products
- Analytics: revenue trend, status split, revenue by category, top sellers, frequently-bought-together pairs

**API** (`/docs` for Swagger UI)
- `GET /api/products/` (search + filters), `GET /api/products/{id}`, `GET /api/products/categories`
- `POST /api/auth/register`, `POST /api/auth/login` (returns a bearer token), `GET /api/auth/me`
- `GET/POST /api/orders/`, `POST /api/orders/{id}/cancel`
- Admin only: `POST/DELETE /api/products/`, `GET /api/orders/all`, `PATCH /api/orders/{id}/status`

## Project structure

```
app.py               Streamlit entry point (sidebar navigation + routing)
ui/                  Streamlit pages (home, product, cart, checkout, orders, admin_*)
services/            Business logic: auth, products, inventory, cart, orders, payments, reviews
models/              Analytics engine and recommender system
utils/               Password hashing, validators, CSV helpers
config/settings.py   Paths, store settings, default admin account
backend/             FastAPI app, schemas, token auth and routes
data/seed_products.csv  Initial product catalogue (copied to data/raw/ on first run)
docker/              Dockerfile + docker-compose.yml
tests/               pytest suite: services, API and every UI page
```

Runtime data lives in `data/raw/*.csv` (created automatically, git-ignored). Delete that folder to reset the store.

## How to run

### 1. Install

```bash
python -m venv venv
venv\Scripts\activate          # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

### 2. Run the Streamlit store

```bash
python -m streamlit run app.py
```

Open http://localhost:8501.

**Default admin login:** `admin@store.com` / `admin123`. Override it with the `ADMIN_EMAIL`, `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables before the first run.

**Demo card:** `4242 4242 4242 4242`, any future expiry (MM/YY), any 3-digit CVV. No real payment is made.

### 3. Run the FastAPI backend (optional)

```bash
python -m uvicorn backend.main:app --reload
```

API docs: http://127.0.0.1:8000/docs (add `--port 8010` if port 8000 is busy). Set `SECRET_KEY` in the environment so tokens survive restarts.

### 4. Run with Docker

```bash
docker compose -f docker/docker-compose.yml up --build
```

- Frontend: http://localhost:8501
- Backend: http://localhost:8000/docs

### 5. Run the tests

```bash
python -m pytest
```

## Tech stack

Python · Streamlit · FastAPI · Pydantic v2 · pandas · Plotly · bcrypt · pytest
