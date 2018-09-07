from django.core.management.base import BaseCommand
from profiles.models import Match


class Command(BaseCommand):
    help = 'Remove all matches'

    def handle(self, *args, **options):
        Match.objects.all().delete()