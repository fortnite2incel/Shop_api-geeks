from datetime import date

from rest_framework.exceptions import ValidationError

MIN_AGE_TO_CREATE_PRODUCT = 18


def _get_birthdate_from_request(request):
    """
    Достаёт claim `birthdate` из JWT токена текущего запроса.

    При аутентификации через JWTAuthentication DRF кладёт распарсенный
    AccessToken в `request.auth` — с ним можно работать как со словарём.
    Если запрос пришёл не по JWT (например, по обычному Token),
    `request.auth` будет либо None, либо не будет поддерживать .get(),
    в этом случае считаем, что дата рождения не указана.
    """
    auth = getattr(request, 'auth', None)
    if auth is None:
        return None

    getter = getattr(auth, 'get', None)
    if getter is None:
        return None

    return getter('birthdate')


def validate_age_from_token(request):
    """
    Валидатор возраста пользователя при создании Product.

    Дата рождения берётся из JWT токена (claim `birthdate`), а не из базы,
    поэтому валидатор работает только при аутентификации через JWT.
    """
    birthdate_raw = _get_birthdate_from_request(request)

    if not birthdate_raw:
        raise ValidationError('Укажите дату рождения, чтобы создать продукт.')

    try:
        birthdate = date.fromisoformat(str(birthdate_raw))
    except (TypeError, ValueError):
        raise ValidationError('Укажите дату рождения, чтобы создать продукт.')

    today = date.today()
    age = today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )

    if age < MIN_AGE_TO_CREATE_PRODUCT:
        raise ValidationError('Вам должно быть 18 лет, чтобы создать продукт.')
