from utils.hashing import hash_password, verify_password
from config.settings import RAW_DATA_DIR
from utils.helpers import load_csv, save_csv
import os
import pandas as pd

USERS_FILE = os.path.join(RAW_DATA_DIR, 'users.csv')

class AuthService:
    def __init__(self):
        self._ensure_users_file()

    def _ensure_users_file(self):
        if not os.path.exists(USERS_FILE):
            df = pd.DataFrame(columns=['username', 'email', 'password_hash', 'id'])
            save_csv(df, USERS_FILE)

    def register_user(self, username, email, password):
        users = load_csv(USERS_FILE)
        if email in users['email'].values:
            return False, "Email already registered"
        
        new_user = pd.DataFrame([{
            'username': username,
            'email': email, 
            'password_hash': hash_password(password),
            'id': len(users) + 1
        }])
        
        users = pd.concat([users, new_user], ignore_index=True)
        save_csv(users, USERS_FILE)
        return True, "Registration successful"

    def login_user(self, email, password):
        users = load_csv(USERS_FILE)
        user = users[users['email'] == email]
        
        if user.empty:
            return None, "User not found"
        
        hashed = user.iloc[0]['password_hash']
        if verify_password(password, hashed):
            return user.iloc[0].to_dict(), "Login successful"
        return None, "Invalid password"
