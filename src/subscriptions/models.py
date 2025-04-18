from django.contrib.auth.models import Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
import helpers
from django.urls import reverse
from helpers.billing import create_product

User = settings.AUTH_USER_MODEL

ALLOW_CUSTOM_GROUPS = True
SUBCRIPTION_PERMISSIONS = [
    ("advanced", "Advanced Perm"),
    ("pro", "Pro Perm"),
    ("basic", "Basic Perm") 
]
# Create your models here.
class Subscription(models.Model):
    """
    Subscription Model
    """
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission, limit_choices_to={'content_type__app_label': 'subscriptions', 'codename__in': [p[0] for p in SUBCRIPTION_PERMISSIONS]})
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    order = models.IntegerField(default=-1, help_text="Order to display the price in the subscription page")
    featured = models.BooleanField(default=True, help_text="Featured price will be shown on the subscription page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    features = models.TextField(blank=True, null=True, help_text="Features for pricing card seperated by new line")

   
    @property
    def stripe_currency(self):
        return "usd"
    
    @property
    def get_features_as_list(self):
        if self.features is None:
            return []
        return [x.strip() for x in self.features.split("\n") if x.strip()]

    def __str__(self):
        return f"{self.name} - {self.active}"

    def get_checkout_url(self):
        return reverse("sub_price_redirect", kwargs={"subscription_price_id": self.id})
    
    class Meta:
        ordering = ['order', 'featured', '-updated']
        permissions = SUBCRIPTION_PERMISSIONS

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = create_product(name=self.name, 
            metadata = {
                "subscription_plan_id": self.id,
            }, raw=False)
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)    

class SubscriptionPrice(models.Model):

    """
    Subscription Price Model
    """

    class IntervalChoices(models.TextChoices):
        MONTHLY = "month" , "Monthly"
        YEARLY = "year" , "Yearly"

    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(max_length=120,default=IntervalChoices.MONTHLY, choices=IntervalChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    order = models.IntegerField(default=-1, help_text="Order to display the price in the subscription page")
    featured = models.BooleanField(default=True, help_text="Featured price will be shown on the subscription page")
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'featured', '-updated']

    @property
    def stripe_currency(self):
        return "usd"

    @property
    def product_stripe_id(self):
        if self.subscription is None:
            return None
        return self.subscription.stripe_id

    @property
    def stripe_price(self):
        return int(self.price * 100) 

    def save(self, *args, **kwargs):
        if (not self.stripe_id and self.subscription is not None): 
            stripe_id = helpers.billing.create_price(
                currency=self.stripe_currency,
                unit_amount=self.stripe_price,
                interval=self.interval,
                product=self.product_stripe_id,
                metadata={"subscription_price_id": self.id}
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(subscription=self.subscription, interval=self.interval).exclude(id=self.id)
            qs.update(featured=False)



class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    active = models.BooleanField(default=True)
   
def user_sub_post_save(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subsciption_obj = user_sub_instance.subscription
    groups_ids = []
    if subsciption_obj is not None:
        groups = subsciption_obj.groups.all()
        groups_ids = groups.values_list("id", flat=True)
    if not ALLOW_CUSTOM_GROUPS:
        user.groups.set(groups_ids)
    else:
        subs_qs = Subscription.objects.filter(active=True)
        if subsciption_obj is not None:
            subs_qs = subs_qs.exclude(id=subsciption_obj.id)
        subs_groups = subs_qs.values_list("groups__id", flat=True)
        subs_groups_set = set(subs_groups)
        current_groups = user.groups.all().values_list("id", flat=True)
        groups_ids_set = set(groups_ids)
        current_groups_set = set(current_groups) -  subs_groups_set
        final_groups_ids = list(groups_ids_set | current_groups_set)
        user.groups.set(final_groups_ids)
    user.save()

post_save.connect(user_sub_post_save, sender=UserSubscription)
