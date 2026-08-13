from django.core.cache import cache

CONFIRMATION_CODE_PREFIX = 'confirmation_code'
CONFIRMATION_CODE_TTL = 60 * 5  # 5 минут


def _cache_key(user_id):
    return f'{CONFIRMATION_CODE_PREFIX}:{user_id}'


def set_confirmation_code(user_id, code):
    """Сохраняет код подтверждения в Redis с временем жизни 5 минут."""
    cache.set(_cache_key(user_id), code, timeout=CONFIRMATION_CODE_TTL)


def get_confirmation_code(user_id):
    """Возвращает код подтверждения из Redis (или None, если истёк/не найден)."""
    return cache.get(_cache_key(user_id))


def delete_confirmation_code(user_id):
    """Удаляет код подтверждения из Redis сразу после использования."""
    cache.delete(_cache_key(user_id))
