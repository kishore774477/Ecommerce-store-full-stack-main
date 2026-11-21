import os

import pandas as pd

from config.settings import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME, USERS_FILE
from utils.hashing import hash_password, verify_password
from utils.helpers import data_lock, load_csv, next_id, save_csv
from utils.validators import validate_email, validate_password_strength, validate_username

USER_COLUMNS = ["id", "username", "email", "password_hash", "role"]


class AuthService:
    def __init__(self):
        self._ensure_users_file()

    def _ensure_users_file(self):
        with data_lock:
            if os.path.exists(USERS_FILE):
                df = load_csv(USERS_FILE)
                if "role" not in df.columns and not df.empty:
                    df["role"] = df["username"].apply(lambda u: "admin" if u == ADMIN_USERNAME else "customer")
                    save_csv(df[USER_COLUMNS], USERS_FILE)
                return
            admin = pd.DataFrame([{
                "id": 1,
                "username": ADMIN_USERNAME,
                "email": ADMIN_EMAIL.lower(),
                "password_hash": hash_password(ADMIN_PASSWORD),
                "role": "admin",
            }])
            save_csv(admin[USER_COLUMNS], USERS_FILE)

    def _load_users(self) -> pd.DataFrame:
        df = load_csv(USERS_FILE)
        if df.empty:
            return pd.DataFrame(columns=USER_COLUMNS)
        df["email"] = df["email"].astype(str).str.lower()
        df["username"] = df["username"].astype(str)
        return df

    @staticmethod
    def _public(row) -> dict:
        """User info safe to keep in the session (no password hash)."""
        return {
            "id": int(row["id"]),
            "username": str(row["username"]),
            "email": str(row["email"]),
            "role": str(row.get("role", "customer")),
        }

    def register_user(self, username, email, password):
        username = (username or "").strip()
        email = (email or "").strip().lower()
        if not validate_username(username):
            return False, "Username must be 3-30 letters, digits, '.', '_' or '-'"
        if not validate_email(email):
            return False, "Invalid email format"
        if not validate_password_strength(password):
            return False, "Password must be at least 8 characters"

        with data_lock:
            users = self._load_users()
            if email in users["email"].values:
                return False, "Email already registered"
            if username.lower() in users["username"].str.lower().values:
                return False, "Username already taken"

            new_user = pd.DataFrame([{
                "id": next_id(users),
                "username": username,
                "email": email,
                "password_hash": hash_password(password),
                "role": "customer",
            }])
            users = pd.concat([users, new_user], ignore_index=True) if not users.empty else new_user
            save_csv(users[USER_COLUMNS], USERS_FILE)
        return True, "Registration successful"

    def login_user(self, email, password):
        email = (email or "").strip().lower()
        if not email or not password:
            return None, "Email and password are required"
        users = self._load_users()
        user = users[users["email"] == email]
        if user.empty:
            return None, "Invalid email or password"
        row = user.iloc[0]
        if verify_password(password, str(row["password_hash"])):
            return self._public(row), "Login successful"
        return None, "Invalid email or password"

    def get_user(self, user_id):
        users = self._load_users()
        user = users[users["id"] == int(user_id)]
        return None if user.empty else self._public(user.iloc[0])

    def get_all_users(self) -> pd.DataFrame:
        users = self._load_users()
        return users.drop(columns=["password_hash"], errors="ignore")

    @staticmethod
    def is_admin(user) -> bool:
        return bool(user) and user.get("role") == "admin"
