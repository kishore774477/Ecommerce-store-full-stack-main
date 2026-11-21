import uuid

from utils.validators import luhn_check, validate_cvv, validate_expiry


class PaymentService:
    """Simulated payment gateway. No card data is stored anywhere.

    In a real app this would call Stripe/Razorpay/PayPal.
    Test card: 4242 4242 4242 4242, any future expiry, any 3-digit CVV.
    """

    def process_payment(self, amount, card_number="", expiry="", cvv="", method="Card"):
        if amount is None or amount <= 0:
            return False, "Invalid amount", None

        if method == "Cash on Delivery":
            return True, "Order will be paid on delivery", f"COD-{uuid.uuid4().hex[:10].upper()}"

        card_number = (card_number or "").replace(" ", "").replace("-", "")
        if not luhn_check(card_number):
            return False, "Invalid card number", None
        if not validate_expiry(expiry):
            return False, "Invalid or expired card (use MM/YY)", None
        if not validate_cvv(cvv):
            return False, "Invalid CVV", None

        return True, f"Payment of ${amount:,.2f} successful", f"TXN-{uuid.uuid4().hex[:12].upper()}"
