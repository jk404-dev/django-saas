from django.http import HttpResponse
from django.shortcuts import render
from visits.models import PageVisit


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
