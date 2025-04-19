from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from helpers.billing import start_checkout_session, get_checkout_session, get_subscription, get_checkout_customer_plan, cancel_subscription
from django.urls import reverse
from subscriptions.models import Subscription
from subscriptions.models import SubscriptionPrice
from subscriptions.models import UserSubscription
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

User = get_user_model()

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
    if not session_id:
        return HttpResponse("Missing session ID.")
        
    customer_id, stripe_id, sub_stripe_id, current_period_start, current_period_end = get_checkout_customer_plan(session_id)
    
    try:
        price_obj = SubscriptionPrice.objects.get(stripe_id=stripe_id) 
    except SubscriptionPrice.DoesNotExist:
         print(f"ERROR: Price object not found for stripe_id {stripe_id}")
         return HttpResponse("Price configuration error.")
    except SubscriptionPrice.MultipleObjectsReturned:
         print(f"ERROR: Multiple Price objects found for stripe_id {stripe_id}")
         return HttpResponse("Duplicate price configuration error.")

    sub_obj = None
    if price_obj:
        try:
            sub_obj = price_obj.subscription
            if sub_obj is None:
                print(f"ERROR: Price object {price_obj.id} (Stripe: {stripe_id}) is not linked to a Subscription.")
                return HttpResponse("Configuration error: Price not linked to plan.")
        except AttributeError:
            print("ERROR: SubscriptionPrice model is missing the 'subscription' relationship.")
            return HttpResponse("Internal model configuration error.")
    else:
        print("ERROR: price_obj is None, cannot derive subscription.")
        return HttpResponse("Failed to find price object.")

    user_obj = None
    try:
        user_obj = User.objects.get(customer__stripe_id=customer_id)
    except User.DoesNotExist:
        print(f"ERROR: User object not found for customer_id {customer_id}")
        user_obj = None
    except User.MultipleObjectsReturned:
        print(f"ERROR: Multiple User objects found for customer_id {customer_id}")
        return HttpResponse("Duplicate user configuration error.")
    except AttributeError:
        print(f"ERROR: Cannot query User via 'customer__stripe_id'. Check User/Customer model relationships.")
        return HttpResponse("Internal model query error.")

    _user_sub_exists = False
    _user_sub_obj = None
    
    try:
        with transaction.atomic(): 
            if not user_obj:
                print("ERROR: user_obj is None inside transaction block.")
                raise ValueError("Cannot proceed without a valid user object.")

            try:
                _user_sub_obj = UserSubscription.objects.select_for_update().get(user=user_obj) 
                _user_sub_exists = True
            except UserSubscription.DoesNotExist:
                _user_sub_exists = False 
            except UserSubscription.MultipleObjectsReturned:
                print(f"ERROR: Multiple UserSubscriptions found for user {user_obj.id} within transaction.")
                raise ValueError("User subscription data inconsistent.")

            if sub_obj is None:
                print("ERROR: sub_obj is None inside transaction block.")
                raise ValueError("Cannot associate null subscription.")

            if not _user_sub_exists:
                _user_sub_obj = UserSubscription.objects.create(
                    user=user_obj, 
                    subscription=sub_obj,
                    stripe_id=sub_stripe_id,
                    current_period_start=current_period_start,
                    current_period_end=current_period_end
                )
                print(f"Created UserSubscription for {user_obj.id} with Stripe ID {sub_stripe_id} within transaction.")
            
            elif _user_sub_obj: 
                if _user_sub_obj.subscription != sub_obj:
                    old_stripe_id = _user_sub_obj.stripe_id
                    if old_stripe_id is not None:
                        try:
                            cancel_subscription(old_stripe_id)
                            print(f"Cancelled old Stripe subscription {old_stripe_id}")
                        except Exception as cancel_err:
                            print(f"ERROR cancelling old Stripe subscription {old_stripe_id}: {cancel_err}")
                            raise ValueError(f"Failed to cancel old Stripe subscription {old_stripe_id}. Halting update.") from cancel_err

                    _user_sub_obj.subscription = sub_obj
                    _user_sub_obj.stripe_id = sub_stripe_id
                    _user_sub_obj.current_period_start = current_period_start
                    _user_sub_obj.current_period_end = current_period_end
                    _user_sub_obj.save()
                    print(f"Updated UserSubscription for {user_obj.id} to {sub_obj.name} with Stripe ID {sub_stripe_id} within transaction.")
                
                elif _user_sub_obj.stripe_id != sub_stripe_id:
                    print(f"WARN: UserSubscription for {user_obj.id} has same plan but different Stripe ID (DB: {_user_sub_obj.stripe_id}, New: {sub_stripe_id}). Updating ID.")
                    _user_sub_obj.stripe_id = sub_stripe_id
                    _user_sub_obj.current_period_start = current_period_start
                    _user_sub_obj.current_period_end = current_period_end
                    _user_sub_obj.save() 

                else:
                    print(f"UserSubscription already up to date for {user_obj.id} (Stripe ID: {sub_stripe_id}) within transaction.")

    except ValueError as e: 
        print(f"TRANSACTION ROLLED BACK due to ValueError: {e}")
        return HttpResponse(str(e)) 
    except Exception as e: 
        print(f"TRANSACTION ROLLED BACK due to Exception: {e}")
        return HttpResponse("Failed to save subscription details due to database error.")

    if _user_sub_obj is None:
         print("ERROR: _user_sub_obj is unexpectedly None after transaction block.")
         return HttpResponse("Final subscription state error after transaction.")

    context = {
        "subscription": sub_obj,
        "price_obj": price_obj,
        "user_obj": user_obj,
    }
    return render(request, "checkouts/success.html", context)


    