from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float = Field(gt=0)
    category: str
    stock: int = Field(ge=0, default=0)
    image: Optional[str] = ""


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class User(UserBase):
    id: int
    role: str = "customer"


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User


class OrderCreate(BaseModel):
    items: Dict[int, int] = Field(description="product_id -> quantity")
    address: str = Field(min_length=5)
    payment_method: str = "Cash on Delivery"


class OrderItem(BaseModel):
    product_id: int
    name: str
    quantity: int
    price: float


class Order(BaseModel):
    id: int
    user_id: int
    total_amount: float
    status: str
    created_at: str
    address: str
    payment_method: str
    items: List[OrderItem]


class StatusUpdate(BaseModel):
    status: str
