from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from profiles.models import Profile
import threading
import logging


class UserProfileInactiveException(Exception):
    pass


class EmailThread(threading.Thread):
    def __init__(self, subject, plain_message, from_email, recipient_list, html_message):
        self.subject = subject
        self.plain_message = plain_message
        self.from_email = from_email
        self.recipient_list = recipient_list
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            self.plain_message,
            self.from_email,
            self.recipient_list,
            html_message=self.html_message
        )


def send_firechickens_email(email_address, subject, body_template, custom_context={}, check_user_profile_active=True, async=False):
    if check_user_profile_active:
        user = User.objects.filter(email=email_address)[0]
        print('user: %s' % user)
        if Profile.objects.get(user=user).inactive:
            raise UserProfileInactiveException('profile with email %s is inactive' % email_address)

    context = {
        'domain': 'firechickens.net',
        'protocol': 'https',
    }
    context.update(custom_context)
    html_message = render_to_string(body_template, context)
    plain_message = strip_tags(html_message)
    print('Sending email with subject %s to address %s' % (subject, email_address))
    logging.info('Sending email with subject %s to address %s' % (subject, email_address))
    if async:
        EmailThread(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [email_address],
            html_message=html_message
        ).start()
    else:
        send_mail(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [email_address], html_message=html_message)
