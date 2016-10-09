from django.views.generic import View, FormView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from markdown import markdown

from .models import Mail

from .forms import MailModelForm

from bs4 import BeautifulSoup


class UnsubscribeWithIdView(View):
    pass


class UnsubscribeDoneView(View):
    pass


class NewslettersIndexView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('newsletter.create_mail', 'newsletter.change_mail', 'newsletter.delete_mail')
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'newsletter/newsletters_index.html'

    def get(self, request):
        sent_mail = Mail.objects.all().order_by('-date_created')

        # TODO: Get the sent mails
        return render(request, self.template_name, {'sent_mail': sent_mail})


class SendEmailDoneView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('newsletter.create_mail', 'newsletter.change_mail', 'newsletter.delete_mail')
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'newsletter/send_mail_done.html'

    def get(self, request):
        return render(request, template_name=self.template_name)


class SendEmailView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = ('newsletter.create_mail', 'newsletter.change_mail', 'newsletter.delete_mail')
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'newsletter/send_mail.html'
    success_url = 'done/'
    form_class = MailModelForm

    def form_valid(self, form):
        email = form.save(commit=False)

        # TODO: Append an unsubscribe link to the end (per-email basis)

        email_html = markdown(email.text)
        email_text = ''.join(BeautifulSoup(email_html, 'html5lib').findAll(text=True))

        # TODO: Send the email (celery task)

        return super(SendEmailView, self).form_valid(form)


class SentEmailIndexView(LoginRequiredMixin, View):
    # TODO: Need a mechanism to check for correct permissions here
    pass


class SentEmailDetailView(LoginRequiredMixin, View):
    # TODO: Need a mechanism to check for correct permissions here
    pass
