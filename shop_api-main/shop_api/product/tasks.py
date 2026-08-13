import json
import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task
def send_low_rating_alert(review_id):
    """
    Задача, использующая SMTP: отправляет модераторам письмо о том, что
    товару поставили низкую оценку (1-2 звезды).

    Запускается асинхронно через .delay() из product.views.review_list_api_view.
    """
    from users.models import CustomUser
    from product.models import Review

    try:
        review = Review.objects.select_related('product').get(id=review_id)
    except Review.DoesNotExist:
        logger.warning('Review %s не найден для отправки уведомления', review_id)
        return

    moderator_emails = list(
        CustomUser.objects.filter(is_staff=True, is_active=True).values_list('email', flat=True)
    )
    if not moderator_emails:
        return

    send_mail(
        subject=f'Низкая оценка товара «{review.product.title}»',
        message=(
            f'Товару "{review.product.title}" поставили оценку {review.stars}/5.\n'
            f'Комментарий: {review.text or "—"}'
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=moderator_emails,
        fail_silently=True,
    )


@shared_task
def generate_daily_products_report():
    """
    Задача, запускаемая по расписанию (Celery Beat, crontab): раз в сутки
    формирует отчёт по продуктам и отзывам за последние 24 часа и
    сохраняет его в файл (пример "сгенерировать что-то" задачи).
    """
    from django.db.models import Avg
    from product.models import Product, Review

    since = timezone.now() - timedelta(days=1)

    report = {
        'generated_at': timezone.now().isoformat(),
        'products_total': Product.objects.count(),
        'reviews_last_24h': Review.objects.filter(created_at__gte=since).count(),
        'average_rating': Product.objects.aggregate(avg=Avg('reviews__stars'))['avg'],
    }

    report_path = settings.BASE_DIR / 'reports'
    report_path.mkdir(exist_ok=True)
    file_path = report_path / f'products_report_{timezone.now():%Y-%m-%d}.json'
    file_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))

    logger.info('Сформирован отчёт по продуктам: %s', file_path)
    return str(file_path)
