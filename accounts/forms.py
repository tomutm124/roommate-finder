from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class RegisterForm(forms.ModelForm):
    username = forms.CharField(
        validators=[RegexValidator(r'^[a-z]*$', 'Please enter a valid ITSC (e.g. tmchanaa).')]
    )

    class Meta:
        model = User
        fields = ('username',)

