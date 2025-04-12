from django.contrib import admin
from django.contrib.auth.models import Group, Permission
# Register your models here.
from .models import Subscription, UserSubscription

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    filter_horizontal = ['groups', 'permissions']
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "permissions":
            kwargs["queryset"] = Permission.objects.all().order_by('content_type__app_label', 'name')
        return super().formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(Subscription, SubscriptionAdmin)

class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'content_type']
    list_filter = ['content_type__app_label']
    search_fields = ['name', 'codename']
    ordering = ['content_type__app_label', 'codename']

admin.site.register(Permission, PermissionAdmin)

class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription', 'active']
    list_filter = ['subscription']
    search_fields = ['user__username', 'subscription__name']
    ordering = ['user__username', 'subscription__name']

admin.site.register(UserSubscription, UserSubscriptionAdmin)
