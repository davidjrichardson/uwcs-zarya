from django.views.generic import View, FormView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .forms import MailModelForm


class UnsubscribeWithIdView(View):
    pass


class UnsubscribeDoneView(View):
    pass


class SendEmailDoneView(LoginRequiredMixin, View):
    # TODO: Need a mechanism to check for correct permissions here
    pass


class SendEmailView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = ('newsletter.create_mail', 'newsletter.change_mail', 'newsletter.delete_mail')
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'newsletter/send_mail.html'
    success_url = 'done/'
    form_class = MailModelForm


class SentEmailIndexView(LoginRequiredMixin, View):
    # TODO: Need a mechanism to check for correct permissions here
    pass


class SentEmailDetailView(LoginRequiredMixin, View):
    # TODO: Need a mechanism to check for correct permissions here
    pass
