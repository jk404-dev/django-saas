import stripe
from dotenv import load_dotenv
import os
from helpers.date_utils import timestamp_as_datetime

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

def start_checkout_session(customer_id,
        success_url="",
        cancel_url="",
        price_stripe_id="",
        raw=True):
    if not success_url.endswith("?session_id={CHECKOUT_SESSION_ID}"):
        success_url = f"{success_url}" + "?session_id={CHECKOUT_SESSION_ID}"
    response = stripe.checkout.Session.create(
        customer=customer_id,
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[{"price": price_stripe_id, "quantity": 1}],
        mode="subscription",
    )
    if raw:
        return response
    return response.url

def get_checkout_session(stripe_id, raw=True):
    response = stripe.checkout.Session.retrieve(stripe_id)
    if raw:
        return response
    return response.url

def get_subscription(stripe_id, raw=True):
    response = stripe.Subscription.retrieve(stripe_id)
    if raw:
        return response
    return response.url

def cancel_subscription(stripe_id, raw=True):
    try:
        response = stripe.Subscription.delete(stripe_id)
        if raw:
            return response 
        return response.status 
    except stripe.error.StripeError as e:
        print(f"ERROR cancelling Stripe subscription {stripe_id}: {e}")
        raise e 

def get_checkout_customer_plan(session_id):
    checkout_r = get_checkout_session(session_id, raw=True)
    customer_id = checkout_r.customer
    sub_stripe_id = checkout_r.subscription
    sub_r = get_subscription(sub_stripe_id, raw=True)
    
    current_period_start = None
    current_period_end = None
    sub_plan = sub_r.plan
    
    # Last resort: use created date and billing cycle attributes
    if current_period_start is None and hasattr(sub_r, 'created'):
        try:
            current_period_start = timestamp_as_datetime(sub_r.created)
            print(f"DEBUG: Using created date for period start: {current_period_start}")
        except Exception as e:
            print(f"DEBUG: Error using created date: {str(e)}")
    
    if current_period_end is None and hasattr(sub_r, 'billing_cycle_anchor') and hasattr(sub_r.plan, 'interval'):
        import datetime
        anchor = timestamp_as_datetime(sub_r.billing_cycle_anchor)
        interval = sub_r.plan.interval
                
        if interval == 'month':
            current_period_end = anchor + datetime.timedelta(days=30)
        elif interval == 'year':
            current_period_end = anchor + datetime.timedelta(days=365)
        elif interval == 'week':
            current_period_end = anchor + datetime.timedelta(days=7)
        elif interval == 'day':
            current_period_end = anchor + datetime.timedelta(days=1)
    
    return customer_id, sub_plan.id, sub_stripe_id, current_period_start, current_period_end