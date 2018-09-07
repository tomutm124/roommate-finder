from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.utils.http import urlsafe_base64_decode
from .models import Profile, Message
from .forms import ProfileModelForm, MessageModelForm
from .mixin import AddUserToPreferenceMixin, UniquePerUserMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    UpdateView,
    ListView,
)
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from core.email import send_firechickens_email, UserProfileInactiveException
import datetime


MESSAGE_COOL_DOWN = datetime.timedelta(minutes=5)


class ProfileCreateView(LoginRequiredMixin, AddUserToPreferenceMixin, UniquePerUserMixin, CreateView):
    model = Profile
    form_class = ProfileModelForm
    template_name = "profiles/create.html"
    success_url = reverse_lazy("profiles:create_success")


def create_success_view(request):
    return render(request, "profiles/created.html")


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileModelForm
    template_name = "profiles/update.html"
    success_url = reverse_lazy("profiles:update_success")

    def get_object(self, queryset=None):
        try:
            obj = self.request.user.profile
        except Profile.DoesNotExist:
            raise Http404
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_inactive_button'] = True
        return context


def update_success_view(request):
    return render(request, "profiles/updated.html")


@login_required
def profile_self_detail_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return render(request, 'profiles/no_profile.html')
    context = {
        'object': profile
    }
    return render(request, 'profiles/self_profile_detail.html', context)


@login_required
def profile_detail_view(request, uid):
    pk = int(urlsafe_base64_decode(uid).decode())
    profile = Profile.objects.get(pk=pk)
    context = {
        'object': profile,
        'uid': uid,
    }
    return render(request, 'profiles/profile_detail.html', context)


class ProfileListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        qs = self.request.user.profile.match1s
        return qs.order_by('-score')

    template_name = 'profiles/matches.html'


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageModelForm
    template_name = "profiles/message.html"
    success_url = reverse_lazy("profiles:message_sent")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        try:
            sender_profile = self.request.user.profile
        except Profile.DoesNotExist:
            form.add_error(None, "You must have a profile before sending a message.")
            return self.form_invalid(form)

        receiver_uid = self.kwargs.get('uid')
        if receiver_uid is None:
            form.add_error(None, "Invalid user.")
            return self.form_invalid(form)

        receiver_pk = int(urlsafe_base64_decode(receiver_uid).decode())
        try:
            receiver_profile = Profile.objects.get(pk=receiver_pk)
        except Profile.DoesNotExist:
            form.add_error(None, "Invalid user.")
            return self.form_invalid(form)

        form.instance.sender = sender_profile
        form.instance.receiver = receiver_profile

        cool_down_cutoff_time = timezone.now() - MESSAGE_COOL_DOWN
        if Message.objects.filter(sender=sender_profile, receiver=receiver_profile, sent_time__gte=cool_down_cutoff_time).exists():
            form.add_error(None, "You can only send a message to the same user every 5 minutes. Please wait.")
            return self.form_invalid(form)

        if receiver_profile.inactive:
            form.add_error(None, "This user's profile is no longer active, you cannot send him/her a message.")
            return self.form_invalid(form)
        else:
            # send email
            subject = 'New Message on Fire Chickens'
            template = 'profiles/new_message_email.html'
            try:
                send_firechickens_email(
                    receiver_profile.user.email,
                    subject,
                    template,
                    {'username': sender_profile.display_name},
                    async=True
                )
            except UserProfileInactiveException:
                form.add_error(None, "This user's profile is no longer active, you cannot send him/her a message.")
                return self.form_invalid(form)
        print("Sending email for message...")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        receiver_uid = self.kwargs.get('uid')
        if receiver_uid is None:
            display_name = '***Invalid User***'
        else:
            receiver_pk = int(urlsafe_base64_decode(receiver_uid).decode())
            try:
                receiver_profile = Profile.objects.get(pk=receiver_pk)
                display_name = receiver_profile.display_name
            except Profile.DoesNotExist:
                display_name = '***Invalid User***'
        context['display_name'] = display_name
        return context


def message_sent_view(request):
    return render(request, "profiles/message_sent.html")


@login_required
def message_detail_view(request, message_id):
    pk = int(urlsafe_base64_decode(message_id).decode())
    message = Message.objects.get(pk=pk)
    user_profile = request.user.profile
    if user_profile == message.sender:
        is_sender = True
    elif user_profile == message.receiver:
        is_sender = False
    else:
        raise Http404
    context = {
        'message': message,
        'is_sender': is_sender,
    }
    return render(request, 'profiles/message_detail.html', context)


@login_required
def received_messages_view(request):
    if hasattr(request.user, 'profile') and request.user.profile:
        messages = Message.objects.filter(receiver=request.user.profile)
        sorted_messages = sorted(messages, key=lambda x: x.sent_time, reverse=True)
        return render(request, 'profiles/messages_received.html', {'messages': sorted_messages})
    else:
        return render(request, 'profiles/messages_received.html', {'messages': []})


@login_required
def sent_messages_view(request):
    if hasattr(request.user, 'profile') and request.user.profile:
        messages = Message.objects.filter(sender=request.user.profile)
        sorted_messages = sorted(messages, key=lambda x: x.sent_time, reverse=True)
        return render(request, 'profiles/messages_sent.html', {'messages': sorted_messages})
    else:
        return render(request, 'profiles/messages_sent.html', {'messages': []})



