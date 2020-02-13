from threading import Thread

from flask import current_app, render_template
from flask_mail import Message
from .extensions import mail

from . import make_celery

celery = make_celery(app=None)


def _send_async_mail(app, message):
    with app.app_context():
        mail.send(message)


@celery.task()
def send_mail(to, subject, template, **kwargs):
    message = Message(current_app.config['ALBUMY_MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    _send_async_mail(app, message)


def send_confirm_email(user, token, to=None):
    send_mail(subject='Email Confirm', to=to or user.email, template='emails/confirm', user=user, token=token)


def send_reset_password_email(user, token):
    send_mail(subject='Password reset', to=user.email, template='emails/reset_password', user=user, token=token)
