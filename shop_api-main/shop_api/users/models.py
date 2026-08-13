from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from users.managers import CustomUserManager
import random
import string


def generate_confirmation_code():
    return ''.join(random.choices(string.digits, k=6))



REGISTRATION_SOURCE_CHOICES = [
    ('local', 'Local'),
    ('google', 'Google'),
    ('facebook', 'Facebook'),
]


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    registration_source = models.CharField(
        max_length=20, choices=REGISTRATION_SOURCE_CHOICES, default='local'
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"] 

    def clean(self):
        super().clean()
        # Подстраховка на уровне модели (например, при редактировании через админку)
        if self.is_superuser and not self.phone_number:
            raise ValidationError(
                {'phone_number': 'Номер телефона обязателен для суперпользователя'}
            )

    def __str__(self):
        return self.email


# Модель ConfirmationCode больше не используется — коды подтверждения
# теперь хранятся в Redis (см. users/services.py) с TTL 5 минут.