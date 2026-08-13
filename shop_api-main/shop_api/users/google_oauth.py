import requests
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import CustomUser
from users.serializers import OauthCodeSerializer

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


class GoogleLoginAPIView(APIView):
    """
    Авторизация/регистрация через Google OAuth 2.0.

    Принимает `code`, полученный на фронтенде после согласия пользователя
    (Authorization Code flow), обменивает его на access_token в Google,
    получает профиль пользователя и создаёт/логинит пользователя в системе.

    При входе через Google:
    - пользователь становится активным (is_active=True);
    - обновляется дата последнего входа (last_login);
    - first_name/last_name берутся из given_name/family_name;
    - registration_source выставляется в "google" при первой регистрации.
    """

    permission_classes = []
    authentication_classes = []

    def post(self, request):
        serializer = OauthCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code']

        token_response = requests.post(
            GOOGLE_TOKEN_URL,
            data={
                'code': code,
                'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_OAUTH_REDIRECT_URI,
                'grant_type': 'authorization_code',
            },
            timeout=10,
        )

        if token_response.status_code != 200:
            return Response(
                {'error': 'Не удалось получить токен Google', 'details': token_response.text},
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = token_response.json().get('access_token')

        userinfo_response = requests.get(
            GOOGLE_USERINFO_URL,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10,
        )

        if userinfo_response.status_code != 200:
            return Response(
                {'error': 'Не удалось получить данные пользователя Google'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = userinfo_response.json()
        email = data.get('email')
        if not email:
            return Response(
                {'error': 'Google не вернул email пользователя'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user, created = CustomUser.objects.get_or_create(
            email=email,
            defaults={
                'first_name': data.get('given_name', ''),
                'last_name': data.get('family_name', ''),
                'registration_source': 'google',
            },
        )

        if not created:
            user.first_name = data.get('given_name', user.first_name)
            user.last_name = data.get('family_name', user.last_name)

        user.is_active = True
        user.last_login = timezone.now()
        user.save()

        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['is_active'] = user.is_active
        refresh['birthdate'] = str(user.birthdate) if user.birthdate else None

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'created': created,
        })
