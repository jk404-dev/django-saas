from django.conf import settings
from django.db import models
from helpers.billing import create_customer

from allauth.account.signals import (
    user_signed_up as allauth_user_signed_up,
    email_confirmed as allauth_email_confirmed,
)

# Create your models here.
User = settings.AUTH_USER_MODEL
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    init_email = models.EmailField(null=True, blank=True)
    init_email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email
    
    def save(self, *args, **kwargs):
        if not self.stripe_id:
            if self.init_email_confirmed and self.init_email:     
                email = self.init_email
                if email != "" or email is not None:
                    stripe_id = create_customer(email=email, 
                    metadata = {
                        "customer_id": self.user.id,
                        "customer_email": self.user.email,
                    }, raw=False)
                    self.stripe_id = stripe_id
        super().save(*args, **kwargs)

def allauth_user_signed_up_handler(request, user, **kwargs):
    email = user.email
    Customer.objects.create(
        user=user,
        init_email=email,
        init_email_confirmed=False,
    )

allauth_user_signed_up.connect(allauth_user_signed_up_handler)

def allauth_email_confirmed_handler(request, email_address, **kwargs):
    qs = Customer.objects.filter(
        init_email=email_address.email,
        init_email_confirmed=False,
    )
    for obj in qs:
        obj.init_email_confirmed = True
        obj.save()

allauth_email_confirmed.connect(allauth_email_confirmed_handler)
