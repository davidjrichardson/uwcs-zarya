from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin


class UnsubscribeWithIdView(View):
    pass


class UnsubscribeDoneView(View):
    pass


class SendEmailDoneView(LoginRequiredMixin, View):
    # TODO: Need a mechanism to check for correct permissions here
    pass


class SendEmailView(LoginRequiredMixin, View):
    # TODO: Need a mechanism to check for correct permissions here
    pass


class SentEmailIndexView(LoginRequiredMixin, View):
    # TODO: Need a mechanism to check for correct permissions here
    pass


class SentEmailDetailView(LoginRequiredMixin, View):
    # TODO: Need a mechanism to check for correct permissions here
    pass
