from stripe import Stripe
from ..config import settings

# Initialize Stripe client
stripe = Stripe(settings.stripe_secret_key)
