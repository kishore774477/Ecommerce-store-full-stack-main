import time

class PaymentService:
    def process_payment(self, amount, card_number, expiry, cvv):
        """
        Simulate payment processing.
        In a real app, this would integrate with Stripe/PayPal.
        """
        # Simulate network delay
        time.sleep(1)
        
        # Basic validation mock
        if not card_number or not expiry or not cvv:
            return False, "Invalid payment details"
            
        if amount <= 0:
            return False, "Invalid amount"
            
        # Success mock
        return True, f"Payment of ${amount:.2f} successful"
