from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^unsubscribe/(?P<token>[A-Fa-f0-9]{64})/$', views.UnsubscribeWithIdView.as_view(), name='unsub_with_id'),
    url(r'^sent/(?P<email_id>[0-9]+)/$', views.SentEmailDetailView.as_view(), name='sent_email_detail'),
    url(r'^send/done/$', views.SendEmailDoneView.as_view(), name='send_email_done'),
    url(r'^send/$', views.SendEmailView.as_view(), name='send_email'),
    url(r'^$', views.NewslettersIndexView.as_view(), name='newsletters_index')
]