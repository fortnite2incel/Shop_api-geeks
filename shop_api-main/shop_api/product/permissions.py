from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """
    Разрешение для модераторов (сотрудников).

    Правила:
    - Модератор обязательно должен иметь is_staff=True.
    - Модератор может просматривать, изменять и удалять ЧУЖИЕ продукты.
    - Модератору запрещено создавать продукты (метод POST).
    """

    message = 'Требуются права модератора (is_staff=True).'

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated and user.is_staff):
            return False

        if request.method == 'POST':
            self.message = 'Модераторам запрещено создавать продукты.'
            return False

        return True

    def has_object_permission(self, request, view, obj):
        # На уровне объекта достаточно снова убедиться, что это модератор.
        # Модератору разрешено работать с продуктами вне зависимости от того,
        # кто является их владельцем (в т.ч. с чужими).
        user = request.user
        return bool(user and user.is_authenticated and user.is_staff)


class IsOwner(BasePermission):
    """Разрешение для владельца продукта (обычный пользователь)."""

    message = 'Вы можете изменять и удалять только свои продукты.'

    def has_object_permission(self, request, view, obj):
        return bool(
            request.user
            and request.user.is_authenticated
            and obj.owner_id == request.user.id
        )
