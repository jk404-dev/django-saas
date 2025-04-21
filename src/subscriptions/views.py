from django.shortcuts import render, redirect
from subscriptions.models import SubscriptionPrice, UserSubscription
from django.contrib.auth.decorators import login_required
import helpers.billing as billing
from django.contrib.auth.models import User
# Create your views here.
def subscription_price_view(request):
    qs = SubscriptionPrice.objects.filter(featured=True)
    monthly_qs = SubscriptionPrice.objects.filter(interval=SubscriptionPrice.IntervalChoices.MONTHLY)
    yearly_qs = SubscriptionPrice.objects.filter(interval=SubscriptionPrice.IntervalChoices.YEARLY)
    return render(request, 'subscriptions/pricing.html', {'qs': qs, 'monthly_qs': monthly_qs, 'yearly_qs': yearly_qs})

def select_plan_view(request, stripe_id):
    plan = SubscriptionPrice.objects.get(stripe_id=stripe_id)
    return render(request, 'subscriptions/select_plan.html', {'plan': plan})

@login_required
def user_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user) 
    # if request.method == 'POST':
    #     if user_sub_obj.stripe_id:
    #         sub_data = billing.get_subscription(user_sub_obj.stripe_id, raw=True)
    #         for key, value in sub_data.items():
    #             setattr(user_sub_obj, key, value)
    #         user_sub_obj.save()
    return render(request, 'subscriptions/user_detail_view.html', {'user_sub_obj': user_sub_obj})

@login_required
def cancel_subscription_view(request):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if user_sub_obj.status != 'active':
        return redirect('home')
    if request.method == 'POST':
        if user_sub_obj.status == 'active':
            billing.cancel_subscription(user_sub_obj.stripe_id, raw=True)
            user_sub_obj.status = 'cancelled'
            user_sub_obj.active = False
            user_sub_obj.save()
            return redirect('user_subscription')
    return render(request, 'subscriptions/cancel_subscription.html', {'user_sub_obj': user_sub_obj})



