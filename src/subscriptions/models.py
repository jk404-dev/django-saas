from django.contrib.auth.models import Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
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
    name = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group)
    permissions = models.ManyToManyField(Permission, limit_choices_to={'content_type__app_label': 'subscriptions', 'codename__in': [p[0] for p in SUBCRIPTION_PERMISSIONS]})
    stripe_id = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.active}"

    class Meta:
        permissions = SUBCRIPTION_PERMISSIONS

    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = create_product(name=self.name, 
            metadata = {
                "subscription_plan_id": self.id,
            }, raw=False)
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)    

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
