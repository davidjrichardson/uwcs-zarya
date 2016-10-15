from django.views.generic import View, FormView
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from markdown import markdown

from .models import Mail, Subscription
from .forms import MailModelForm
from .tasks import send_newsletter


class UnsubscribeWithIdView(View):
    template_name = 'newsletter/unsubscribe.html'

    def get(self, request, token):
        subscription = get_object_or_404(Subscription, unsubscribe_token=token)
        subscription.delete()

        return render(request, self.template_name, {'email': subscription.email})


class NewslettersIndexView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('newsletter.create_mail', 'newsletter.change_mail', 'newsletter.delete_mail')
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'newsletter/newsletters_index.html'

    def get(self, request):
        sent_mail = Mail.objects.all().order_by('-date_created')

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
        email = form.save()
        send_newsletter.delay(email.id)

        return super(SendEmailView, self).form_valid(form)


class SentEmailDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = ('newsletter.create_mail', 'newsletter.change_mail', 'newsletter.delete_mail')
    login_url = '/accounts/login/'
    redirect_field_name = 'redirect_to'
    template_name = 'newsletter/newsletter_detail.html'

    def get(self, request, email_id):
        newsletter = get_object_or_404(Mail, id=email_id)

        return render(request, self.template_name,
                      {'newsletter': newsletter, 'newsletter_html': markdown(newsletter.text)})
