from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from services.product_service import ProductService

from ..schemas import Product, ProductCreate
from ..security import get_admin_user

router = APIRouter()


def _to_products(df) -> List[Product]:
    return [Product(**row) for row in df.to_dict("records")]


@router.get("/", response_model=List[Product])
def list_products(
    q: Optional[str] = Query(None, description="Search in name/description"),
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    df = ProductService().search_products(q or "", category, min_price, max_price)
    return _to_products(df)


@router.get("/categories", response_model=List[str])
def list_categories():
    return ProductService().get_categories()


@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    product = ProductService().get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=Product, status_code=201)
def create_product(payload: ProductCreate, _admin: dict = Depends(get_admin_user)):
    service = ProductService()
    ok, msg, new_id = service.add_product(**payload.model_dump())
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return service.get_product_by_id(new_id)


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, _admin: dict = Depends(get_admin_user)):
    ok, msg = ProductService().delete_product(product_id)
    if not ok:
        raise HTTPException(status_code=404, detail=msg)
