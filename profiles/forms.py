from .models import Profile, Message
from django import forms


class ProfileModelForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'display_name',
            'hall',
            'gender',
            'llc',
            'llc_weight',
            'llc_required',
            'room_type',
            'room_type_required',
            'room_type_weight',
            'language1',
            'language2',
            'language_required',
            'language_weight',
            'bedtime_start',
            'bedtime_end',
            'bedtime_required',
            'bedtime_weight',
            'nine_am_class_mon',
            'nine_am_class_tue',
            'nine_am_class_wed',
            'nine_am_class_thu',
            'nine_am_class_fri',
            'nine_am_class_penalty',
            'year',
            'year_required',
            'year_weight',
            'school',
            'school_required',
            'school_weight',
            'major',
            'major_weight',
            'remarks',
            'minimum_weight',
            'allow_non_match_to_contact',
            'inactive',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        form_control_fields = [
            forms.fields.CharField,
            forms.fields.TypedChoiceField,
            forms.fields.IntegerField,
        ]
        form_check_input_fields = [
            forms.fields.BooleanField,
        ]
        for key, value in self.fields.items():
            if type(value) in form_control_fields:
                value.widget.attrs.update({'class' : 'form-control'})
            elif type(value) in form_check_input_fields:
                value.widget.attrs.update({'class' : 'form-check-input'})


class MessageModelForm(forms.ModelForm):
    content = forms.CharField(
        max_length=1000,
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Message...', 'class': 'form-control'}),
    )

    class Meta:
        model = Message
        fields = [
            'content'
        ]





