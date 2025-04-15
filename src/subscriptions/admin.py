from django.contrib import admin
from django.contrib.auth.models import Group, Permission
# Register your models here.
from .models import Subscription, UserSubscription, SubscriptionPrice

class SubscriptionPriceInline(admin.TabularInline):
    model = SubscriptionPrice
    readonly_fields = ['id', 'stripe_id', 'product_stripe_id', 'stripe_price']
    can_delete = False
    extra = 0

class SubscriptionPriceAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'price', 'interval']
    list_filter = ['subscription', 'interval']
    search_fields = ['subscription__name']

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    filter_horizontal = ['groups', 'permissions']
    inlines = [SubscriptionPriceInline]
    readonly_fields = ['stripe_id']
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "permissions":
            kwargs["queryset"] = Permission.objects.all().order_by('content_type__app_label', 'name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'content_type']
    list_filter = ['content_type__app_label']
    search_fields = ['name', 'codename']
    ordering = ['content_type__app_label', 'codename']


class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription', 'active']
    list_filter = ['subscription']
    search_fields = ['user__username', 'subscription__name']
    ordering = ['user__username', 'subscription__name']

admin.site.register(Subscription, SubscriptionAdmin)

admin.site.register(Permission, PermissionAdmin)

admin.site.register(SubscriptionPrice, SubscriptionPriceAdmin)

admin.site.register(UserSubscription, UserSubscriptionAdmin)
