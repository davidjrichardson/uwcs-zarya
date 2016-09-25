from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^event/(?P<event_id>[0-9]+)/signup/$', views.EventSignupView.as_view(), name='event_signup'),
    url(r'^event/(?P<event_id>[0-9]+)/unsignup/$', views.EventUnsignupView.as_view(), name='event_unsignup'),
    url(r'^feed.ics$', views.EventFeed(), name='ical_feed'),
]