FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Позволяет запускать 'python manage.py ...', 'celery -A shop_api.shop_api ...'
# и gunicorn из /app без дополнительных манипуляций с sys.path.
ENV PYTHONPATH=/app:/app/shop_api

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . .
