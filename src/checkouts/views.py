from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from helpers.billing import start_checkout_session, get_checkout_session, get_subscription
from django.urls import reverse

from subscriptions.models import SubscriptionPrice
# Create your views here.
def product_price_redirect_view(request, subscription_price_id=None, *args, **kwargs):
    request.session['checkout_subscription_price_id'] = subscription_price_id
    return redirect("stripe-checkout_start")

@login_required
def checkout_redirect_view(request):
    checkout_subscription_price_id = request.session.get('checkout_subscription_price_id')
    try:
        obj = SubscriptionPrice.objects.get(stripe_id=checkout_subscription_price_id)
    except:
        obj = None
    if obj is None or checkout_subscription_price_id is None:
        return redirect("pricing")
    customer_stripe_id = request.user.customer.stripe_id
    success_url = request.build_absolute_uri(reverse("stripe-checkout_success"))
    cancel_url = request.build_absolute_uri(reverse("pricing"))
    price_stripe_id = obj.stripe_id

    url = start_checkout_session(customer_stripe_id, success_url=success_url, cancel_url=cancel_url, price_stripe_id=price_stripe_id, raw=False)
    return redirect(url)

def checkout_finalize_view(request):
    session_id = request.GET.get("session_id")
    checkout_r = get_checkout_session(session_id, raw=True)
    customer_id = checkout_r.customer
    sub_stripe_id = checkout_r.subscription
    sub_r = get_subscription(sub_stripe_id, raw=True)
    sub_plan = sub_r.plan
    sub_plan_price_stripe_id = sub_plan.id
    price_qs = SubscriptionPrice.objects.filter(stripe_id=sub_plan_price_stripe_id)
    price_obj = price_qs.first()
    context = {
        "subscription": sub_r,
        "checkout": checkout_r,
        "price_obj": price_obj,

    }
    return render(request, "checkouts/success.html", context)


    