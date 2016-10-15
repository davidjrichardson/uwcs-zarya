from django.utils import timezone
from django.views.generic import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from django_ical.views import ICalFeed

from .models import EventSignup, EventPage


class EventFeed(ICalFeed):
    product_id = '-//uwcs.co.uk//Events//EN'
    timezone = 'GMT'
    file_name = 'events.ics'

    def items(self):
        return EventPage.objects.filter(finish__gte=timezone.now()).order_by('-start')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_start_datetime(self, item):
        return item.start

    def item_end_datetime(self, item):
        return item.finish

    def item_location(self, item):
        return item.location

    def item_link(self, item):
        return 'https://uwcs.co.uk' + item.get_url_parts()[2]


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
