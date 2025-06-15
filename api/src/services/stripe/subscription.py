import stripe
from ...config import settings

class StripeSubscriptionService:
    def __init__(self):
        self.stripe = stripe
        self.stripe.api_key = settings.stripe_secret_key
        self.price_ids = {
            "basic": settings.stripe_price_id_basic,
            "pro": settings.stripe_price_id_pro,
            "enterprise": settings.stripe_price_id_enterprise
        }
        
    def create_subscription(self, customer_id, price_id, metadata=None):
        """
        Create a subscription for a customer
        """
        try:
            subscription = self.stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata=metadata,
                expand=["latest_invoice.payment_intent"]
            )
            return subscription
        except Exception as e:
            print(f"Error creating subscription: {str(e)}")
            raise
            
    def get_subscription(self, subscription_id):
        """
        Get a subscription by ID
        """
        try:
            return self.stripe.Subscription.retrieve(subscription_id)
        except Exception as e:
            print(f"Error retrieving subscription: {str(e)}")
            return None
            
    def update_subscription(self, subscription_id, **kwargs):
        """
        Update a subscription
        """
        try:
            return self.stripe.Subscription.modify(subscription_id, **kwargs)
        except Exception as e:
            print(f"Error updating subscription: {str(e)}")
            raise
            
    def cancel_subscription(self, subscription_id):
        """
        Cancel a subscription
        """
        try:
            return self.stripe.Subscription.delete(subscription_id)
        except Exception as e:
            print(f"Error canceling subscription: {str(e)}")
            raise
            
    def get_subscription_plans(self):
        """
        Get available subscription plans
        """
        plans = {
            "basic": {
                "id": "basic",
                "name": "Basic Plan",
                "price_id": self.price_ids["basic"],
                "features": [
                    "10 product analyses per month",
                    "Basic product recommendations",
                    "Standard support"
                ]
            },
            "pro": {
                "id": "pro",
                "name": "Pro Plan",
                "price_id": self.price_ids["pro"],
                "features": [
                    "50 product analyses per month",
                    "Advanced product recommendations",
                    "Priority support",
                    "Market trend analysis"
                ]
            },
            "enterprise": {
                "id": "enterprise",
                "name": "Enterprise Plan",
                "price_id": self.price_ids["enterprise"],
                "features": [
                    "Unlimited product analyses",
                    "Premium recommendations",
                    "Dedicated support",
                    "Custom integrations",
                    "Bulk analysis"
                ]
            }
        }
        
        return plans
