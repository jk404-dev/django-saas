from django.contrib.auth.models import Group, Permission
from django.db import models


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
    
    class Meta:
        permissions = SUBCRIPTION_PERMISSIONS
