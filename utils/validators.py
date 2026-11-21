import re
from datetime import date


def validate_email(email: str) -> bool:
    """Validates an email address."""
    pattern = r"^[\w\.\+-]+@[\w\.-]+\.\w+$"
    return bool(email) and re.match(pattern, email.strip()) is not None


def validate_password_strength(password: str) -> bool:
    """Validates that a password is at least 8 characters long."""
    return bool(password) and len(password) >= 8


def validate_username(username: str) -> bool:
    """3-30 characters: letters, digits, underscore, dot or hyphen."""
    return bool(username) and re.match(r"^[\w\.-]{3,30}$", username.strip()) is not None


def luhn_check(card_number: str) -> bool:
    """Standard Luhn checksum used by card numbers."""
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 12 or len(digits) > 19:
        return False
    checksum = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def validate_expiry(expiry: str, today: date = None) -> bool:
    """Accepts MM/YY and rejects expired dates."""
    match = re.match(r"^(0[1-9]|1[0-2])/(\d{2})$", (expiry or "").strip())
    if not match:
        return False
    today = today or date.today()
    month, year = int(match.group(1)), 2000 + int(match.group(2))
    return (year, month) >= (today.year, today.month)


def validate_cvv(cvv: str) -> bool:
    return bool(re.match(r"^\d{3,4}$", (cvv or "").strip()))
