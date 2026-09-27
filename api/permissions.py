from rest_framework.permissions import BasePermission

from .models import Company


class IsAdminUser(BasePermission):
    """Allow access only to users whose Company role is ADMIN."""

    message = 'You must be a platform admin to access this endpoint.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'company')
            and request.user.company.role == Company.Role.ADMIN
        )
