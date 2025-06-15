import stripe
from ...config import settings

class StripeCustomerService:
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = settings.stripe_secret_key
        
    def create_customer(self, email, name=None, metadata=None):
        """
        Create a new Stripe customer
        """
        try:
            customer = self.stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata
            )
            return customer
        except Exception as e:
            print(f"Error creating Stripe customer: {str(e)}")
            raise
            
    def get_customer(self, customer_id):
        """
        Get a Stripe customer by ID
        """
        try:
            return self.stripe.Customer.retrieve(customer_id)
        except Exception as e:
            print(f"Error retrieving Stripe customer: {str(e)}")
            return None
            
    def update_customer(self, customer_id, **kwargs):
        """
        Update a Stripe customer
        """
        try:
            return self.stripe.Customer.modify(customer_id, **kwargs)
        except Exception as e:
            print(f"Error updating Stripe customer: {str(e)}")
            raise
            
    def delete_customer(self, customer_id):
        """
        Delete a Stripe customer
        """
        try:
            return self.stripe.Customer.delete(customer_id)
        except Exception as e:
            print(f"Error deleting Stripe customer: {str(e)}")
            raise
