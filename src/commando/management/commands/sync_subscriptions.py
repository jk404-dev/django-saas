from customers.models import Customer
import helpers.billing
from django.core.management.base import BaseCommand
from subscriptions.models import UserSubscription

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        customer_objs = Customer.objects.filter(stripe_id__isnull=False)
        for customer_obj in customer_objs:
            print(customer_obj.user.email)
            stripe_id = customer_obj.stripe_id
            stripe_subscriptions = helpers.billing.get_customer_active_subscriptions(stripe_id)
            for sub in stripe_subscriptions:
                existing_user_subs_qs = UserSubscription.objects.filter(stripe_id__iexact=f"{sub.id}".strip())
                if existing_user_subs_qs.exists():
                    continue
                helpers.billing.cancel_subscription(sub.id)
                print(sub.id, existing_user_subs_qs.exists())
