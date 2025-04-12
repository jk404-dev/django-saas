from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from visits.models import PageVisit
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

LOGIN_URL = settings.LOGIN_URL


def home_page_view(request):
    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)
    PageVisit.objects.create(path=request.path)
    return render(request, 'home.html', {'page_qs': page_qs, 'qs': qs})

def about_page_view(request):
    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)
    PageVisit.objects.create(path=request.path)
    return render(request, 'home.html', {'page_qs': page_qs, 'qs': qs})

VALID_CODE = '1234'

def pw_protected_view(request):
    is_allowed = request.session.get('protected_page_allowed')
    if request.method == 'POST':
        user_pw_sent = request.POST.get('code') 
        if user_pw_sent == VALID_CODE:
            is_allowed = True
            request.session['protected_page_allowed'] = is_allowed
    if is_allowed:
        return render(request, 'protected/view.html')
    else:
        return render(request, 'protected/entry.html')

