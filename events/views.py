from django.views.generic import View, RedirectView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import EventSignup, EventPage


class EventSignupView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'events/event_signup.html'
    already_done_template = 'events/event_already_signedup.html'

    def post(self, request, event_id):
        event = get_object_or_404(EventPage, page_ptr_id=event_id)

        if EventSignup.objects.filter(event=event, member=request.user).first():
            return render(request, self.already_done_template, {
                'event': event
            })

        signup = EventSignup(member=request.user, event=event, comment=request.POST.get('comment', ''))
        signup.save()

        return render(request, self.template_name, {
            'event': event
        })


class EventUnsignupView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'events/event_unsignup.html'
    already_done_template = 'events/event_already_unsignedup.html'

    def get(self, request, event_id):
        event = get_object_or_404(EventPage, page_ptr_id=event_id)

        signup = EventSignup.objects.filter(event=event, member=request.user).first()

        if not signup:
            return render(request, self.already_done_template, {
                'event': event
            })
        else:
            signup.delete()

            return render(request, self.template_name, {
                'event': event
            })
