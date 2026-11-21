from fastapi import APIRouter, Depends, HTTPException

from services.auth_service import AuthService

from ..schemas import LoginRequest, Token, User, UserCreate
from ..security import create_token, get_current_user

router = APIRouter()


@router.post("/register", response_model=User, status_code=201)
def register(payload: UserCreate):
    service = AuthService()
    ok, msg = service.register_user(payload.username, payload.email, payload.password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    user, _ = service.login_user(payload.email, payload.password)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest):
    user, msg = AuthService().login_user(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail=msg)
    return {"access_token": create_token(user["id"]), "token_type": "bearer", "user": user}


@router.get("/me", response_model=User)
def me(user: dict = Depends(get_current_user)):
    return user
