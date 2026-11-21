from datetime import date

from models.analytics import AnalyticsEngine
from models.recommender import RecommenderSystem
from services.auth_service import AuthService
from services.cart_service import CartService
from services.inventory_service import InventoryService
from services.order_service import OrderService
from services.payment_service import PaymentService
from services.product_service import ProductService
from services.review_service import ReviewService
from utils.helpers import parse_items
from utils.validators import luhn_check, validate_expiry


def test_seed_products_loaded():
    products = ProductService().get_all_products()
    assert len(products) == 20
    assert {"id", "name", "price", "stock", "image"} <= set(products.columns)


def test_default_admin_and_registration():
    auth = AuthService()
    admin, _ = auth.login_user("admin@store.com", "admin123")
    assert admin and admin["role"] == "admin"
    assert "password_hash" not in admin

    ok, _ = auth.register_user("alice", "Alice@Example.com", "password1")
    assert ok
    ok, msg = auth.register_user("alice2", "alice@example.com", "password1")
    assert not ok and "Email" in msg
    ok, msg = auth.register_user("ALICE", "other@example.com", "password1")
    assert not ok and "Username" in msg

    user, _ = auth.login_user("alice@example.com", "password1")
    assert user["username"] == "alice" and user["role"] == "customer" and user["id"] == 2
    assert auth.login_user("alice@example.com", "wrong-pass")[0] is None


def test_cart_totals():
    cart = {}
    svc = CartService()
    svc.add_to_cart(cart, 1, 2)
    svc.add_to_cart(cart, 12)
    total = svc.get_cart_total(cart, ProductService())
    assert total == round(1999.99 * 2 + 24.99, 2)
    svc.update_quantity(cart, 1, 0)
    assert 1 not in cart


def test_order_deducts_and_cancel_restores_stock():
    AuthService()
    inv = InventoryService()
    before = inv.get_stock(20)  # Basketball, stock 3
    orders = OrderService()
    ok, msg, order_id = orders.create_order(1, {20: 2, 1: 1}, "221B Baker Street")
    assert ok, msg
    assert inv.get_stock(20) == before - 2

    ok, msg, _ = orders.create_order(1, {20: 5}, "221B Baker Street")
    assert not ok and "Only" in msg

    ok, _ = orders.cancel_order(order_id, 1)
    assert ok
    assert inv.get_stock(20) == before
    ok, msg = orders.update_status(order_id, "Shipped")
    assert not ok


def test_order_total_is_computed_server_side():
    ok, _, order_id = OrderService().create_order(1, {12: 2}, "Somewhere 123")
    assert ok
    row = OrderService().get_all_orders().iloc[0]
    assert row["total_amount"] == round(24.99 * 2, 2)
    assert parse_items(row["items"]) == {12: 2}


def test_parse_items_legacy_format():
    assert parse_items("{1: 2, 3: 1}") == {1: 2, 3: 1}
    assert parse_items('{"1": 2}') == {1: 2}
    assert parse_items("__import__('os').system('x')") == {}


def test_payment_validation():
    pay = PaymentService()
    assert pay.process_payment(10, "4242 4242 4242 4242", "12/99", "123")[0]
    assert not pay.process_payment(10, "4242 4242 4242 4241", "12/99", "123")[0]
    assert not pay.process_payment(10, "4242424242424242", "01/20", "123")[0]
    assert pay.process_payment(10, method="Cash on Delivery")[0]
    assert luhn_check("4242424242424242")
    assert not validate_expiry("13/30")
    assert validate_expiry("11/26", today=date(2026, 11, 22))


def test_reviews_one_per_user():
    rs = ReviewService()
    rs.add_review(1, 5, 4, "Good", "bob")
    rs.add_review(1, 5, 2, "Changed my mind", "bob")
    rs.add_review(1, 6, 5, "Great", "carol")
    avg, count = rs.get_average_rating(1)
    assert count == 2 and avg == 3.5


def test_analytics_and_recommender():
    orders = OrderService()
    orders.create_order(2, {1: 1, 8: 2}, "Addr 12345")
    orders.create_order(3, {8: 1, 9: 1}, "Addr 12345")
    _, _, cancelled = orders.create_order(3, {4: 1}, "Addr 12345")
    orders.update_status(cancelled, "Cancelled")

    products = ProductService().get_all_products()
    df = orders.get_all_orders()
    engine = AnalyticsEngine(df, products)
    assert engine.get_orders_count() == 2  # cancelled excluded
    assert round(engine.get_total_sales(), 2) == round(1999.99 + 2 * 129.99 + 129.99 + 49.99, 2)
    top = engine.get_top_products(1)
    assert top.iloc[0]["name"] == "Apple AirPods"

    rec = RecommenderSystem(products, df)
    assert rec.recommend_popular(1).iloc[0]["id"] == 8
    similar = rec.recommend_similar(8, n=3)["id"].tolist()
    assert similar[0] in (1, 9)
