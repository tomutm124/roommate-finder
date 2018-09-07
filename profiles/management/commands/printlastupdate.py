from django.core.management.base import BaseCommand
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from profiles.models import Match, Profile, Message
import pytz


def encode_pk(value):
    return urlsafe_base64_encode(force_bytes(value)).decode()


def convert_to_hkt(value):
    if value:
        hkt = pytz.timezone('Asia/Hong_Kong')
        return value.astimezone(hkt)
    else:
        return None


def format_to_time(value):
    if value:
        return value.strftime('%H:%M')
    else:
        return None


class Command(BaseCommand):
    help = 'Print last updated time for matches and profiles'

    def handle(self, *args, **options):
        for match in Match.objects.all():
            print(match)
            print(convert_to_hkt(match.last_updated).strftime('%H:%M on %d %b (%a)'))
            print()

        for profile in Profile.objects.all():
            print(profile)
            print(encode_pk(profile.id))
            print(convert_to_hkt(profile.last_updated).strftime('%H:%M on %d %b (%a)'))
            print(format_to_time(convert_to_hkt(profile.bedtime_start)))
            print(format_to_time(convert_to_hkt(profile.bedtime_end)))
            print()

        for message in Message.objects.all():
            print("message")
            print(encode_pk(message.id))
            print(convert_to_hkt(message.sent_time).strftime('%H:%M on %d %b (%a)'))

