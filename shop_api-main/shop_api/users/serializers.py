from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.services import get_confirmation_code, delete_confirmation_code

User = get_user_model()


class OauthCodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["is_active"] = user.is_active
        # Дата рождения кладётся в токен, чтобы её можно было использовать
        # в валидаторах (например, проверка возраста при создании Product)
        # без обращения к базе данных.
        token["birthdate"] = str(user.birthdate) if user.birthdate else None
        return token


class UserBaseSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class AuthValidateSerializer(UserBaseSerializer):
    pass


class RegisterValidateSerializer(UserBaseSerializer):
    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise ValidationError('User уже существует!')
        return email


class ConfirmationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user_id = attrs.get('user_id')
        code = attrs.get('code')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError('User не существует!')

        stored_code = get_confirmation_code(user_id)

        if stored_code is None:
            raise ValidationError('Код подтверждения не найден или истёк!')

        if stored_code != code:
            raise ValidationError('Неверный код подтверждения!')

        attrs['user'] = user
        return attrs
