from django.shortcuts import render
import django.contrib.auth.views as auth_views
from .forms import RegisterForm
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from core.email import send_firechickens_email


import secrets
import string


def random_password_generator(size=12):
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(size))


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # check if this ITSC is already registered
            if User.objects.filter(username=user.username).exists():
                form.add_error(None, "There is already an account with this ITSC. Please login instead.")
                return render(request, 'accounts/register.html', {'form': form})

            user.email = user.username + "@connect.ust.hk"

            # set a random password and email
            password = random_password_generator()
            user.set_password(password)
            user.save()
            # send email
            subject = 'Your Account at Fire Chickens'
            template = 'accounts/register_success_email.html'
            send_firechickens_email(
                user.email,
                subject,
                template,
                {'password': password},
                check_user_profile_active=False,
                async=True
            )

            return render(request, 'accounts/check_email.html')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


class CustomPasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'accounts/change-password.html'
    success_url = reverse_lazy('accounts:change_password_success')


def password_change_success(request):
    return render(request, 'accounts/change_password_success.html')


class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'accounts/reset_password.html'
    email_template_name = 'accounts/plain_reset_password_email.html'
    subject_template_name = 'accounts/reset_password_email_subject.txt'
    success_url = reverse_lazy('accounts:reset_password_sent')
    html_email_template_name = 'accounts/reset_password_email.html'

class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'accounts/reset_password_sent.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'accounts/reset_password_confirm.html'
    success_url = reverse_lazy('accounts:reset_password_success')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'accounts/reset_password_success.html'

