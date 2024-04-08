from feed.models import User
from celery import shared_task
from django.contrib.auth.forms import PasswordResetForm


@shared_task
def send_reset_email_async(subject_template_name, email_template_name, context,
                           from_email, to_email, html_email_template_name):
    context['user'] = User.objects.get(pk=context['user'])

    PasswordResetForm.send_mail(
        None,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name
    )


@shared_task
def send_register_email_async(user_id, subject, message, from_email):
    user = User.objects.get(pk=user_id)
    user.email_user(subject, message, from_email)

