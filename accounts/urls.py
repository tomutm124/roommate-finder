from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name="register"),
    path('login/', auth_views.login, {'template_name': 'accounts/login.html'}, name="login"),
    path('logout/', auth_views.logout, {'next_page': '/'}, name='logout'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path('change-password-success/', views.password_change_success, name='change_password_success'),
    path('reset-password/', views.CustomPasswordResetView.as_view(), name='reset_password'),
    path('reset-password-sent/', views.CustomPasswordResetDoneView.as_view(), name='reset_password_sent'),
    path(
        'reset/<str:uidb64>/<str:token>/',
        views.CustomPasswordResetConfirmView.as_view(),
        name='reset_password_confirm'
    ),
    path('reset-success/', views.CustomPasswordResetCompleteView.as_view(), name='reset_password_success'),
]

