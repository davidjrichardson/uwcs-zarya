from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^unsubscribe/(?P<email_id>[0-9]+)/$', views.UnsubscribeWithIdView.as_view(), name='unsub_with_id'),
    url(r'^unsubscribe/done/$', views.UnsubscribeDoneView.as_view(), name='unsub_done'),
    url(r'^sent/(?P<email_id>[0-9]+)/$', views.SentEmailDetailView.as_view(), name='sent_email_detail'),
    url(r'^send/done/$', views.SendEmailDoneView.as_view(), name='send_email_done'),
    url(r'^send/$', views.SendEmailView.as_view(), name='send_email'),
    url(r'^sent/$', views.SentEmailIndexView.as_view(), name='sent_email_index')
]