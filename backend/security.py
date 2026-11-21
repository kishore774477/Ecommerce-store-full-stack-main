"""Minimal signed bearer tokens (HMAC-SHA256) — no extra dependencies.

Set SECRET_KEY in the environment for anything beyond local development.
"""
import base64
import hashlib
import hmac
import json
import os
import secrets
import time

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.auth_service import AuthService

SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
TOKEN_TTL_SECONDS = 60 * 60 * 8

_bearer = HTTPBearer(auto_error=False)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_token(user_id: int) -> str:
    payload = _b64(json.dumps({"sub": user_id, "exp": int(time.time()) + TOKEN_TTL_SECONDS}).encode())
    sig = _b64(hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{sig}"


def decode_token(token: str):
    try:
        payload, sig = token.split(".")
        expected = _b64(hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        data = json.loads(_unb64(payload))
        if data["exp"] < time.time():
            return None
        return int(data["sub"])
    except (ValueError, KeyError, json.JSONDecodeError):
        return None


def get_current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> dict:
    user_id = decode_token(creds.credentials) if creds else None
    user = AuthService().get_user(user_id) if user_id else None
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token",
                            headers={"WWW-Authenticate": "Bearer"})
    return user


def get_admin_user(user: dict = Depends(get_current_user)) -> dict:
    if not AuthService.is_admin(user):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin only")
    return user
