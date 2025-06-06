"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import home_page_view, about_page_view, pw_protected_view, dashboard_page_view  
from subscriptions import views as subscription_views
from checkouts import views as checkout_views

urlpatterns = [
    path('', home_page_view, name='home'),
    path('about/', about_page_view, name='about'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('accounts/billing/', subscription_views.user_subscription_view, name='user_subscription'),
    path('accounts/billing/cancel/', subscription_views.cancel_subscription_view, name='cancel_subscription'),
    path('dashboard/', dashboard_page_view, name='dashboard'),
    path('protected/', pw_protected_view, name='pw_protected_view'),
    path('profiles/', include('profiles.urls')),
    path('pricing/', subscription_views.subscription_price_view, name='pricing'),
    path('checkout/sub-price/<str:subscription_price_id>/', checkout_views.product_price_redirect_view, name='sub_price_redirect'),
    path('checkout/start/', checkout_views.checkout_redirect_view, name='stripe-checkout_start'),
    path('checkout/success/', checkout_views.checkout_finalize_view, name='stripe-checkout_success'),
]
