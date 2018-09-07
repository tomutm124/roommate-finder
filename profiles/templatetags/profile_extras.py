from django import template
from django.template.defaultfilters import stringfilter
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from itertools import compress
import pytz

register = template.Library()


def convert_to_hkt(value):
    hkt = pytz.timezone('Asia/Hong_Kong')
    return value.astimezone(hkt)


@register.filter
@stringfilter
def encode_pk(value):
    return urlsafe_base64_encode(force_bytes(value)).decode()


@register.filter
def bool_to_yes_no(value):
    return 'Yes' if value else 'No'


@register.filter
def datetime_to_time(value):
    if value:
        return convert_to_hkt(value).strftime('%H:%M')
    else:
        return "N/A"


@register.filter
def morning_class_days(value):
    days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri')
    day_filters = (
        value.nine_am_class_mon,
        value.nine_am_class_tue,
        value.nine_am_class_wed,
        value.nine_am_class_thu,
        value.nine_am_class_fri,
    )
    days_with_morning_class = compress(days, day_filters)
    if days_with_morning_class:
        return ', '.join(days_with_morning_class)
    else:
        return 'No'


@register.filter
def show_date(value):
    if value:
        return convert_to_hkt(value).strftime('%d %b, %Y (%a)')
    else:
        return "N/A"


@register.filter
def show_datetime(value):
    if value:
        return convert_to_hkt(value).strftime('%H:%M on %d %b (%a)')
        # return value.strftime('%H:%M on %d %b (%a)')
    else:
        return "N/A"
