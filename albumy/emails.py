from flask import current_app, render_template
from flask_mail import Message
from .extensions import mail
from . import create_celery_app

celery = create_celery_app()


@celery.task(serializer='pickle')
def _send_async_mail(message):
    mail.send(message)


def send_mail(to, subject, template, **kwargs):
    message = Message(current_app.config['ALBUMY_MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.html = render_template(template + '.html', **kwargs)
    _send_async_mail(message)


def send_confirm_email(user, token, to=None):
    send_mail(subject='Email Confirm', to=to or user.email, template='emails/confirm', user=user, token=token)


def send_reset_password_email(user, token):
    send_mail(subject='Password reset', to=user.email, template='emails/reset_password', user=user, token=token)
