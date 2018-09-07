from django.contrib import admin
from django.urls import path
from . import views


app_name = 'profiles'

urlpatterns = [
    path('', views.profile_self_detail_view, name="self"),
    path('create/', views.ProfileCreateView.as_view(), name="create"),
    path('update/', views.ProfileUpdateView.as_view(), name="update"),
    path('create-success/', views.create_success_view, name="create_success"),
    path('update-success/', views.update_success_view, name="update_success"),
    path('view/<str:uid>/', views.profile_detail_view, name="detail"),
    path('message/<str:uid>/', views.MessageCreateView.as_view(), name="message"),
    path('message-sent', views.message_sent_view, name="message_sent"),
    path('message/sent', views.sent_messages_view, name="sent_messages"),
    path('message/received', views.received_messages_view, name="received_messages"),
    path('message/details/<str:message_id>/', views.message_detail_view, name="message_detail"),

]
