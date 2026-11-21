"""Renders every Streamlit page headlessly and checks none of them raise."""
import os

import pytest
from streamlit.testing.v1 import AppTest

from services.auth_service import AuthService
from services.order_service import OrderService
from services.review_service import ReviewService

APP = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")

PAGES = ["home", "login", "register", "product_page", "cart", "checkout", "order_history",
         "admin_dashboard", "admin_orders", "admin_inventory", "admin_analytics"]


def _seed_activity():
    auth = AuthService()
    auth.register_user("erin", "erin@example.com", "password1")
    orders = OrderService()
    orders.create_order(2, {1: 1, 8: 2}, "Addr 12345")
    orders.create_order(2, {8: 1, 9: 1}, "Addr 12345")
    ReviewService().add_review(1, 2, 5, "Great laptop", "erin")


@pytest.mark.parametrize("page", PAGES)
@pytest.mark.parametrize("role", ["guest", "customer", "admin"])
def test_page_renders(page, role):
    _seed_activity()
    at = AppTest.from_file(APP, default_timeout=30)
    at.session_state["page"] = page
    at.session_state["selected_product"] = 1
    at.session_state["cart"] = {1: 1, 12: 2}
    if role == "customer":
        at.session_state["user"] = AuthService().login_user("erin@example.com", "password1")[0]
    elif role == "admin":
        at.session_state["user"] = AuthService().login_user("admin@store.com", "admin123")[0]
    at.run()
    assert not at.exception, [e.value for e in at.exception]

    is_admin_page = page.startswith("admin_")
    denied = any("Access denied" in e.value for e in at.error)
    assert denied == (is_admin_page and role != "admin")
