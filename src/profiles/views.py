from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def profile_view(request, username):
    user = request.user
    profile_user_obj = get_object_or_404(User, username=username)
    return render(request, 'profiles/profile.html', {'profile_user_obj': profile_user_obj})

@login_required
def profile_list_view(request):
    context = {
        "object_list": User.objects.all()
    }
    return render(request, 'profiles/list.html', context)

@login_required
def profile_detail_view(request, username):
    user = request.user
    profile_user_obj = get_object_or_404(User, username=username)
    sync_subs = profile_user_obj.sync_subs.all()
    return render(request, 'profiles/detail.html', {
        'profile_user_obj': profile_user_obj,
        'sync_subs': sync_subs
    })
