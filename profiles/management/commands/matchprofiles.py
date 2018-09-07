from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
import datetime
import logging
from collections import defaultdict
from profiles.models import Profile, Match
from core.email import send_firechickens_email, UserProfileInactiveException

# only check profiles last updated after this amount of time ago
PAST_TIME_TO_CHECK = datetime.timedelta(days=2)

logger = logging.getLogger(__name__)


def get_all_active_profiles():
    return Profile.objects.filter(inactive=False)


def get_profiles_to_update(timedelta):
    cutoff_time = timezone.now() - timedelta
    return get_all_active_profiles().filter(last_updated__gte=cutoff_time)


def filter_profiles(profile, other_profiles):
    # use filter to filter required fields
    other_profiles = other_profiles.filter(hall=profile.hall, gender=profile.gender, allow_non_match_to_contact=True)
    other_profiles = other_profiles.exclude(user=profile.user)
    if profile.llc_required and profile.llc:
        other_profiles = other_profiles.filter(llc=profile.llc)
    if profile.room_type_required and profile.room_type:
        other_profiles = other_profiles.filter(room_type=profile.room_type)
    if profile.language_required:
        if profile.language1:
            other_profiles = other_profiles.filter(
                Q(language1=profile.language1) |
                Q(language2=profile.language1)
            )
        if profile.language2:
            other_profiles = other_profiles.filter(
                Q(language1=profile.language2) |
                Q(language2=profile.language2)
            )
    if profile.bedtime_required:
        if profile.bedtime_start:
            other_profiles = other_profiles.filter(bedtime_end__gte=profile.bedtime_start)
        if profile.bedtime_end:
            other_profiles = other_profiles.filter(bedtime_start__lte=profile.bedtime_end)
    if profile.year_required and profile.year:
        other_profiles = other_profiles.filter(year=profile.year)
    if profile.school_required and profile.school:
        other_profiles = other_profiles.filter(school=profile.school)
    return other_profiles


def nine_am_class_mismatch_penalty(profile, other_profile):
    penalty = 0
    penalty_per_day = profile.nine_am_class_penalty
    attribute_names = (
        "nine_am_class_mon",
        "nine_am_class_tue",
        "nine_am_class_wed",
        "nine_am_class_thu",
        "nine_am_class_fri",
    )
    for attribute in attribute_names:
        if not getattr(profile, attribute) and getattr(other_profile, attribute):
            penalty += penalty_per_day
    return penalty


def calculate_profile_weight(profile, other_profile):
    weight = 0
    if not profile.llc_required and profile.llc and profile.llc == other_profile.llc:
        weight += profile.llc_weight
    if not profile.room_type_required and profile.room_type and profile.room_type == other_profile.room_type:
        weight += profile.room_type_weight
    if not profile.language_required:
        language1_match = profile.language1 and (profile.language1 == other_profile.language1 or profile.language1 == other_profile.language2)
        language2_match = profile.language2 and (profile.language2 == other_profile.language1 or profile.language2 == other_profile.language2)
        if language1_match or language2_match:
            weight += profile.language_weight
    if not profile.bedtime_required and (profile.bedtime_start or profile.bedtime_end):
        # "<bedtime>_match" evaluates to True if that bedtime field is not filled
        bedtime_start_match = (not profile.bedtime_start) or (other_profile.bedtime_end and profile.bedtime_start <= other_profile.bedtime_end)
        bedtime_end_match = (not profile.bedtime_end) or (other_profile.bedtime_start and profile.bedtime_end >= other_profile.bedtime_start)
        if bedtime_start_match and bedtime_end_match:
            weight += profile.bedtime_weight
    weight -= nine_am_class_mismatch_penalty(profile, other_profile)
    if not profile.year_required and profile.year and profile.year == other_profile.year:
        weight += profile.year_weight
    if not profile.school_required and profile.school and profile.school == other_profile.school:
        weight += profile.school_weight
    if profile.major and profile.major == other_profile.major:
        weight += profile.major_weight
    return weight, (weight >= profile.minimum_weight)


def all_required_fields_matched(profile, other_profile):
    if profile.hall != other_profile.hall or profile.gender != other_profile.gender:
        return False
    if profile.llc and profile.llc_required and profile.llc != other_profile.llc:
        return False
    if profile.room_type and profile.room_type_required and profile.room_type != other_profile.room_type:
        return False
    if profile.language_required:
        other_profile_languages = (other_profile.language1, other_profile.language2)
        profile1_mismatch = profile.language1 and profile.language1 not in other_profile_languages
        profile2_mismatch = profile.language2 and profile.language2 not in other_profile_languages
        if profile1_mismatch or profile2_mismatch:
            return False
    if profile.bedtime_required:
        if not other_profile.bedtime_start and not other_profile.bedtime_end:
            return False
        if profile.bedtime_start and other_profile.bedtime_end and profile.bedtime_start > other_profile.bedtime_end:
            return False
        if profile.bedtime_end and other_profile.bedtime_start and profile.bedtime_end < other_profile.bedtime_start:
            return False
    if profile.year and profile.year_required and profile.year != other_profile.year:
        return False
    if profile.school and profile.school_required and profile.school != other_profile.school:
        return False
    return True


def match_profile(profile, other_profiles):
    # return list of (profile1, profile2, score) tuples
    results = []
    # find match for "profile"
    filtered_other_profiles = filter_profiles(profile, other_profiles)
    for other_profile in filtered_other_profiles:
        score, is_match = calculate_profile_weight(profile, other_profile)
        if is_match:
            results.append((profile, other_profile, score))

    if profile.allow_non_match_to_contact:
        # check if "profile" is a match for each profile in "other_profile"
        for other_profile in other_profiles:
            if all_required_fields_matched(other_profile, profile):
                score, is_match = calculate_profile_weight(other_profile, profile)
                if is_match:
                    results.append((other_profile, profile, score))
    return results


def send_new_match_email(email, matches):
    subject = 'New Roommate Match from Fire Chickens'
    template = 'profiles/match_found_email.html'
    custom_context = {
        'matches': matches
    }
    try:
        send_firechickens_email(email, subject, template, custom_context)
    except UserProfileInactiveException as e:
        logger.error('Error encountered in send_new_match_email: %s', e)


class Command(BaseCommand):
    help = 'Match profiles in database'

    def handle(self, *args, **options):
        # matching logic here
        start_time = timezone.now()
        new_matches_by_email = defaultdict(list)
        profiles_to_update = get_profiles_to_update(PAST_TIME_TO_CHECK)
        all_profiles = get_all_active_profiles()
        for profile in profiles_to_update:
            other_profiles = all_profiles.exclude(user=profile.user)
            matches = match_profile(profile, other_profiles)
            for profile1, profile2, score in matches:
                if Match.objects.filter(profile1=profile1, profile2=profile2).exists():
                    Match.objects.filter(profile1=profile1, profile2=profile2).update(
                        score=score,
                        last_updated=timezone.now()
                    )
                else:
                    new_match = Match(profile1=profile1, profile2=profile2, score=score)
                    new_match.save()
                    new_matches_by_email[profile1.user.email].append(new_match)

        for email, matches in new_matches_by_email.items():
            sorted_matched = sorted(matches, key=lambda x: x.score, reverse=True)
            send_new_match_email(email, sorted_matched)
        Match.objects.filter(last_updated__lt=start_time).delete()



