import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task
def send_otp_email(code, email):
    """
    Задача, использующая SMTP: отправляет пользователю код подтверждения
    на email после регистрации.

    Запускается асинхронно через .delay() из
    users.views.RegistrationAPIView, чтобы не блокировать ответ API.
    """
    send_mail(
        subject='Код подтверждения регистрации',
        message=f'Ваш код подтверждения: {code}\nОн действителен 5 минут.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=True,
    )
    logger.info('Письмо с кодом подтверждения отправлено на %s', email)
