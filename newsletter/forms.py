from django.forms import ModelForm

from .models import Mail


class MailModelForm(ModelForm):
    class Meta:
        model = Mail
        fields = ['subject', 'sender', 'text']
