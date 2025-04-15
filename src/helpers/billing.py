import stripe
from dotenv import load_dotenv
import os

load_dotenv()

DJANGO_DEBUG = os.getenv('DJANGO_DEBUG', default=False)
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', default='')

if "sk_test" in STRIPE_SECRET_KEY and not DJANGO_DEBUG:
    raise ValueError("Stripe secret key is not valid")

stripe.api_key = STRIPE_SECRET_KEY

def create_customer(name="", email="", metadata={}, raw=False):
    response = stripe.Customer.create(
        name= name,
        email= email,
        metadata=metadata,
    )
    if raw:
        return response
    stripe_id = response.id
    return stripe_id


def create_product(name="", metadata={}, raw=False):
    response = stripe.Product.create(
        name= name,
        metadata=metadata,
    )
    if raw:
        return response
    stripe_id = response.id
    return stripe_id

def create_price(currency="usd",
                unit_amount=99.99,
                interval = "month",
                product=None,
                metadata={}):
    if product is None:
        return None
    response = stripe.Price.create(
        currency=currency,
        unit_amount=unit_amount,
        recurring={"interval": interval},
        product=product,
        metadata=metadata,
    )
    return response.id
