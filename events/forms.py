from django.forms import ModelForm

from .models import EventSignup


class EventSignupForm(ModelForm):
    class Meta:
        model = EventSignup
        fields = ['comment']
