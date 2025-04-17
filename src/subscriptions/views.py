from django.shortcuts import render
from subscriptions.models import SubscriptionPrice
# Create your views here.
def subscription_price_view(request):
    qs = SubscriptionPrice.objects.filter(featured=True)
    monthly_qs = SubscriptionPrice.objects.filter(interval=SubscriptionPrice.IntervalChoices.MONTHLY)
    yearly_qs = SubscriptionPrice.objects.filter(interval=SubscriptionPrice.IntervalChoices.YEARLY)
    return render(request, 'subscriptions/pricing.html', {'qs': qs, 'monthly_qs': monthly_qs, 'yearly_qs': yearly_qs})

def select_plan_view(request, stripe_id):
    plan = SubscriptionPrice.objects.get(stripe_id=stripe_id)
    return render(request, 'subscriptions/select_plan.html', {'plan': plan})
