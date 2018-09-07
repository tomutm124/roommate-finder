from django.db import models
from django.conf import settings
import datetime
import pytz


# Create your models here.
def _populate_time_options(start_time):
    options = []
    for i in range(24):
        datetime_obj = start_time + datetime.timedelta(minutes=30) * i
        string_obj = '{:%H:%M}'.format(datetime_obj)
        # time_obj = time(hour=datetime_obj.hour, minute=datetime_obj.minute)
        options.append((datetime_obj, string_obj))
    return options


class Profile(models.Model):
    HALLS = (
        ('I', 'I'),
        ('II', 'II'),
        ('III', 'III'),
        ('IV', 'IV'),
        ('V', 'V'),
        ('VI', 'VI'),
        ('VII', 'VII'),
        ('VIII', 'VIII'),
        ('IX', 'IX'),
        ('TKO', 'TKO'),
    )
    GENDERS = (
        ('F', 'F'),
        ('M', 'M'),
    )
    ROOM_TYPES = (
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Triple', 'Triple'),
        ('Bunk Bed', 'Bunk Bed'),
    )
    LLCS = (
        ('None', 'None'),
        ('Fitness Connection (Hall VI)',) * 2,
        ('Live Green (Hall VI)',) * 2,
        ('Arts a-LIVE (Hall VII)',) * 2,
        ('Creative Affinity (Hall VII)',) * 2,
        ('iVillage (Hall VII)',) * 2,
        ('Entrepreneurship (Hall VII)',) * 2,
    )
    LANGUAGES = (
        ('Cantonese', 'Cantonese'),
        ('Mandarin', 'Mandarin'),
        ('English', 'English'),
        ('Korean', 'Korean'),
    )
    SCHOOLS = (
        ('IPO', 'IPO'),
        ('SBM', 'SBM'),
        ('SENG', 'SENG'),
        ('SHSS', 'SHSS'),
        ('SSCI', 'SSCI'),
    )
    MAJORS = (
        ('---SSCI---',) * 2,
        ('BCB',) * 2,
        ('BIBU',) * 2,
        ('BIOT',) * 2,
        ('BISC',) * 2,
        ('CHEM',) * 2,
        ('DSCT',) * 2,
        ('ENVS',) * 2,
        ('MAEC',) * 2,
        ('MATH',) * 2,
        ('PHYS',) * 2,
        ('---SENG---',) * 2,
        ('AE',) * 2,
        ('BIEN',) * 2,
        ('CENG',) * 2,
        ('CEEV',) * 2,
        ('CIEV',) * 2,
        ('CIVL',) * 2,
        ('COMP',) * 2,
        ('COSC',) * 2,
        ('CPEG',) * 2,
        ('DA',) * 2,
        ('ELEC',) * 2,
        ('IEEM',) * 2,
        ('ISDN',) * 2,
        ('MECH',) * 2,
        ('SUSEE',) * 2,
        ('---SBM---',) * 2,
        ('ACCT',) * 2,
        ('ECOF',) * 2,
        ('ECON',) * 2,
        ('FINA',) * 2,
        ('GBM',) * 2,
        ('GBUS',) * 2,
        ('IS',) * 2,
        ('MARK',) * 2,
        ('MGMT',) * 2,
        ('QFIN',) * 2,
        ('OM',) * 2,
        ('WBB',) * 2,
        ('---SHSS---',) * 2,
        ('GCS',) * 2,
        ('QSA',) * 2,
        ('---IPO---',) * 2,
        ('EVMT',) * 2,
        ('IIM',) * 2,
        ('RMBI',) * 2,
        ('Dual Degree',) * 2,
    )
    YEARS = (
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('>4', '>4'),
    )

    START_BEDTIMES = _populate_time_options(pytz.timezone('Asia/Hong_Kong').localize(datetime.datetime(2018, 1, 1, hour=20)))
    END_BEDTIMES = _populate_time_options(pytz.timezone('Asia/Hong_Kong').localize(datetime.datetime(2018, 1, 1, hour=20)))

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=20)

    hall = models.CharField(max_length=3, choices=HALLS)
    gender = models.CharField(max_length=1, choices=GENDERS)
    llc = models.CharField(max_length=32, verbose_name='LLC', choices=LLCS, default='None')
    llc_required = models.BooleanField()
    llc_weight = models.IntegerField(default=0, choices=[(x, x) for x in range(11)], blank=True)

    room_type = models.CharField(max_length=32, verbose_name='Room Type', choices=ROOM_TYPES, blank=True)
    room_type_required = models.BooleanField()
    room_type_weight = models.IntegerField(default=9, choices=[(x, x) for x in range(11)], blank=True)

    # only languages that you are comfortable to use with your roommate
    language1 = models.CharField(max_length=32, choices=LANGUAGES, verbose_name='First Preferred Language', blank=True)
    language2 = models.CharField(max_length=32, blank=True, choices=LANGUAGES, verbose_name='Second Preferred Language')
    language_required = models.BooleanField()
    language_weight = models.IntegerField(default=7, choices=[(x, x) for x in range(11)])

    # use DateTimeField to make 01:00 later than 23:00
    bedtime_start = models.DateTimeField(choices=START_BEDTIMES, verbose_name='Earliest Bedtime', blank=True, null=True)
    bedtime_end = models.DateTimeField(choices=END_BEDTIMES, verbose_name='Latest Bedtime', blank=True, null=True)
    bedtime_required = models.BooleanField()
    bedtime_weight = models.IntegerField(default=7, choices=[(x, x) for x in range(11)], blank=True)

    nine_am_class_mon = models.BooleanField(verbose_name='Mon')
    nine_am_class_tue = models.BooleanField(verbose_name='Tue')
    nine_am_class_wed = models.BooleanField(verbose_name='Wed')
    nine_am_class_thu = models.BooleanField(verbose_name='Thu')
    nine_am_class_fri = models.BooleanField(verbose_name='Fri')
    # penalty per day of unmatched 9am class
    nine_am_class_penalty = models.IntegerField(default=0, choices=[(x, x) for x in range(11)], blank=True)

    year = models.CharField(max_length=2, choices=YEARS, blank=True)
    year_required = models.BooleanField()
    year_weight = models.IntegerField(default=3, choices=[(x, x) for x in range(11)], blank=True)

    school = models.CharField(max_length=8, choices=SCHOOLS, blank=True)
    school_required = models.BooleanField()
    school_weight = models.IntegerField(default=3, choices=[(x, x) for x in range(11)], blank=True)

    # too many major, currently does not allow major required
    major = models.CharField(max_length=20, choices=MAJORS, blank=True)
    major_weight = models.IntegerField(default=5, choices=[(x, x) for x in range(11)], blank=True)

    # will show in email to potential roommates, optional
    remarks = models.CharField(max_length=256, blank=True)

    minimum_weight = models.IntegerField(default=10)

    last_updated = models.DateTimeField(auto_now=True)

    inactive = models.BooleanField(default=False)

    allow_non_match_to_contact = models.BooleanField(default=True)

    def __str__(self):
        return str(self.display_name)


class Match(models.Model):
    score = models.IntegerField()
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='match1s')
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='match2s')
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s - %s - %s' % (
            self.profile1.display_name,
            self.profile2.display_name,
            self.score
        )


class Message(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.SET_NULL, related_name='sent_messages', null=True)
    receiver = models.ForeignKey(Profile, on_delete=models.SET_NULL, related_name='received_messages', null=True)
    content = models.TextField(max_length=1000)
    sent_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='Pending')
