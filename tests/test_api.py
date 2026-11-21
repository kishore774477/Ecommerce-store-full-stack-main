from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _login(email, password):
    r = client.post("/api/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_root_and_products():
    assert client.get("/").status_code == 200
    r = client.get("/api/products/")
    assert r.status_code == 200 and len(r.json()) == 20
    assert client.get("/api/products/1").json()["name"].startswith("Apple MacBook")
    assert client.get("/api/products/999").status_code == 404
    assert len(client.get("/api/products/", params={"category": "Sports"}).json()) == 3


def test_register_login_and_order_flow():
    r = client.post("/api/auth/register",
                    json={"username": "dave", "email": "dave@example.com", "password": "password1"})
    assert r.status_code == 201, r.text
    headers = _login("dave@example.com", "password1")
    assert client.get("/api/auth/me", headers=headers).json()["username"] == "dave"

    assert client.get("/api/orders/").status_code == 401
    r = client.post("/api/orders/", headers=headers,
                    json={"items": {"12": 2}, "address": "12 Market Road"})
    assert r.status_code == 201, r.text
    order = r.json()
    assert order["total_amount"] == round(24.99 * 2, 2)
    assert order["items"][0]["name"] == "Classic Sun Glasses"
    assert len(client.get("/api/orders/", headers=headers).json()) == 1

    # customers can't use admin endpoints
    assert client.get("/api/orders/all", headers=headers).status_code == 403

    admin = _login("admin@store.com", "admin123")
    r = client.patch(f"/api/orders/{order['id']}/status", headers=admin, json={"status": "Shipped"})
    assert r.status_code == 200 and r.json()["status"] == "Shipped"


def test_admin_create_product():
    admin = _login("admin@store.com", "admin123")
    r = client.post("/api/products/", headers=admin,
                    json={"name": "Yoga Mat", "price": 19.5, "category": "Sports", "stock": 10})
    assert r.status_code == 201, r.text
    assert r.json()["id"] == 21
    assert client.post("/api/products/", json={"name": "x", "price": 1, "category": "y"}).status_code == 401
