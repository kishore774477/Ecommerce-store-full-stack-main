from typing import List

from fastapi import APIRouter, Depends, HTTPException

from services.order_service import OrderService

from ..schemas import Order, OrderCreate, StatusUpdate
from ..security import get_admin_user, get_current_user

router = APIRouter()


def _serialize(service: OrderService, row) -> dict:
    return {
        "id": int(row["id"]),
        "user_id": int(row["user_id"]),
        "total_amount": float(row["total_amount"]),
        "status": row["status"],
        "created_at": str(row["created_at"]),
        "address": row["address"],
        "payment_method": row["payment_method"],
        "items": service.describe_items(row["items"]),
    }


@router.get("/", response_model=List[Order])
def my_orders(user: dict = Depends(get_current_user)):
    service = OrderService()
    return [_serialize(service, r) for _, r in service.get_orders_for_user(user["id"]).iterrows()]


@router.get("/all", response_model=List[Order])
def all_orders(_admin: dict = Depends(get_admin_user)):
    service = OrderService()
    return [_serialize(service, r) for _, r in service.get_all_orders().iterrows()]


@router.post("/", response_model=Order, status_code=201)
def create_order(payload: OrderCreate, user: dict = Depends(get_current_user)):
    if payload.payment_method != "Cash on Delivery":
        raise HTTPException(400, "The API only supports 'Cash on Delivery'")
    service = OrderService()
    ok, msg, order_id = service.create_order(user["id"], payload.items, payload.address,
                                             payload.payment_method, "API")
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    orders = service.get_all_orders()
    return _serialize(service, orders[orders["id"] == order_id].iloc[0])


@router.post("/{order_id}/cancel", response_model=Order)
def cancel_order(order_id: int, user: dict = Depends(get_current_user)):
    service = OrderService()
    ok, msg = service.cancel_order(order_id, user["id"])
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    orders = service.get_all_orders()
    return _serialize(service, orders[orders["id"] == order_id].iloc[0])


@router.patch("/{order_id}/status", response_model=Order)
def update_status(order_id: int, payload: StatusUpdate, _admin: dict = Depends(get_admin_user)):
    service = OrderService()
    ok, msg = service.update_status(order_id, payload.status)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    orders = service.get_all_orders()
    return _serialize(service, orders[orders["id"] == order_id].iloc[0])
