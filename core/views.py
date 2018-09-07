from django.shortcuts import render, redirect
from profiles.models import Profile
import profiles.views

# Create your views here.


def home(request):
    # if authenticated and has profile
    if request.user.is_authenticated:
        try:
            _ = request.user.profile
            return profiles.views.ProfileListView.as_view()(request)
        except Profile.DoesNotExist:
            return redirect("profiles:self")
    else:
        return render(request, 'home.html')