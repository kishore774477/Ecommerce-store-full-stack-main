import re

def validate_email(email: str) -> bool:
    """Validates an email address."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def validate_password_strength(password: str) -> bool:
    """Validates that a password is at least 8 characters long."""
    return len(password) >= 8
